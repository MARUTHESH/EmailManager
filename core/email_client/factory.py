from .gmail_client import GmailClient
from .outlook_client import OutlookClient


class EmailClientFactory:
    @staticmethod
    def get_client(provider: str):
        if provider == "gmail":
            client = GmailClient()
        elif provider == "outlook":
            client = OutlookClient()
        else:
            raise ValueError(f"Unsupported email provider: {provider}")

        client.authenticate()
        return client
