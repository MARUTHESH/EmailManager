# internal imports
import os
import datetime
import json
import requests
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
from typing import List

# third party imports
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# local imports
from core.models import Email
from .base import EmailClient

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailClient(EmailClient):
    def __init__(self):
        self.service = None
        self.creds = None
        self.base_url = "https://gmail.googleapis.com/gmail/v1"

    def authenticate(self):
        creds = None
        if os.path.exists('../config/token.json'):
            creds = Credentials.from_authorized_user_file('../config/token.json', SCOPES)
        else:
            flow = InstalledAppFlow.from_client_secrets_file('../config/credentials.json', SCOPES)
            flow.redirect_uri = 'http://localhost:8080/callback'
            creds = flow.run_local_server(port=0)
            # TODO: Can be saved into db by encrypting it
            with open('../config/token.json', 'w') as token:
                token.write(creds.to_json())

        if creds:
            self.creds = json.loads(creds.to_json())
        self.service = build('gmail', 'v1', credentials=creds)


    def get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.creds['token']}",
            "Content-Type": "application/json"
        }
        return headers

    def refresh_access_token(self):
        data = {
            'client_id': self.creds.get('client_id'),
            'client_secret': self.creds.get('client_secret'),
            'refresh_token': self.creds.get('refresh_token'),
            'grant_type': 'refresh_token'
        }

        response = requests.post('https://oauth2.googleapis.com/token', data=data)
        if response.status_code == 200:
            response_json = response.json()
            self.creds['access_token'] = response_json.get('access_token')
            self.creds['expires_at'] = response_json.get('expires_at')
            self.creds['refresh_token'] = response_json.get('refresh_token')
            self.creds['token_type'] = response_json.get('token_type')
            self.creds['scope'] = response_json.get('scope')
            with open('../config/token.json', 'w') as token:
                token.write(json.dumps(self.creds))
            return True
        return False

    def make_request(self, method, endpoint, **kwargs):
        if not self.creds:
            raise Exception("Credentials not found")

        url = f"{self.base_url}/{endpoint}"
        headers = self.get_headers()

        if kwargs.get('query_params'):
            url = f"{url}?{urlencode(kwargs.pop('query_params'))}"

        if kwargs.get('data'):
            kwargs['data'] = json.dumps(kwargs.pop('data'))

        if not kwargs.get('timeout'):
            # setting timeout to 300 seconds
            kwargs['timeout'] = (3, 300)

        response = requests.request(method, url, headers=headers, **kwargs)

        if response.status_code == 401:
            print("🔄 Token expired, refreshing...")
            if self.refresh_access_token():
                headers = self.get_headers()
                response = requests.request(method, url, headers=headers, **kwargs)
            else:
                raise Exception("Failed to refresh access token")
        return response

    def fetch_emails(self, max_results=20):
        response =  self.make_request('GET', 'users/me/messages', query_params={
            'maxResults': max_results})
        if response.status_code == 200:
            response_json = response.json()
            messages = response_json.get('messages', [])
            emails = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(self.make_request, 'GET', f'users/me/messages/{msg["id"]}',
                                           query_params={'format': 'full'}) for msg in messages]
                for future in futures:
                    msg_data = future.result()
                    if msg_data.status_code == 200:
                        msg_data_json = msg_data.json()
                        headers = msg_data_json['payload']['headers']
                        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                        snippet = msg_data_json.get('snippet', '')
                        received_at = msg_data_json.get("internalDate")  # in milliseconds
                        received_at = datetime.datetime.utcfromtimestamp(int(received_at) / 1000).isoformat() + "Z"
                        emails.append(Email(id=msg_data_json['id'], sender=sender, subject=subject, snippet=snippet, received_at=received_at))
            return emails
        return []

    def mark_as_read(self, email_ids: List[str]):
        response = self.make_request('POST', 'users/me/messages/batchModify', data={
            'removeLabelIds': ['UNREAD'],
            'ids': email_ids
        })
        if response.status_code == 204:
            print(f"Marked {email_ids} emails as read")
        else:
            print(f"Failed to mark {email_ids} emails as read")

    def mark_as_unread(self, email_ids: List[str]):
        response = self.make_request('POST', 'users/me/messages/batchModify', data={
            'addLabelIds': ['UNREAD'],
            'ids': email_ids
        })
        if response.status_code == 204:
            print(f"Marked {email_ids} emails as unread")
        else:
            print(f"Failed to mark {email_ids} emails as unread")

    def move_to_folder(self, folder_to_email_map: dict):
        # Gmail labels work like folders
        for folder, email_ids in folder_to_email_map.items():
            response = self.make_request('POST', 'users/me/messages/batchModify', data={
                'addLabelIds': [folder.upper()],
                'ids': email_ids
            })
            if response.status_code == 204:
                print(f"Moved {email_ids} emails to {folder}")
            else:
                print(f"Failed to move {email_ids} emails to {folder}")
