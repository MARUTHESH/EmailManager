from core.email_client.factory import EmailClientFactory
from core.rule_engine import RuleEngine

if __name__ == "__main__":
    # Step 2: Process emails
    rule_engine = RuleEngine("../config/rules.json")
    rule_engine.fetch_emails_and_categorize()
    rule_engine.process(EmailClientFactory.get_client("gmail"))