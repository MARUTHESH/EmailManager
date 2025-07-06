# Local modules
from core.email_client.factory import EmailClientFactory
from core.email_repository import EmailRepository

if __name__ == "__main__":
    # Step 1: Fetch and store emails
    client = EmailClientFactory.get_client("gmail")
    repo = EmailRepository()
    emails = client.fetch_emails(max_results=500)
    repo.save_emails(emails)
