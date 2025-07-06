from .base import EmailClient

class OutlookClient(EmailClient):
    def authenticate(self):
        raise NotImplementedError("Outlook auth not implemented")

    def fetch_emails(self, max_results=10):
        raise NotImplementedError("Outlook fetch not implemented")