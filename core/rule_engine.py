import json

from core.actions import ActionExecutor
from core.models import Email
from core.email_repository import EmailRepository


def prepare_sql_query_based_on_rules(rule, predicate='AND'):
    field = rule['field']
    operator = rule['operator']
    value = rule['value']
    where_clause = ''

    if field == 'received_at':
        if operator == 'less_than_days':
            where_clause = f"received_at < '{value}'"
        elif operator == 'greater_than_days':
            where_clause = f"received_at > '{value}'"
        elif operator == 'less_than_months':
            where_clause = f"received_at < '{value}'"
        elif operator == 'greater_than_months':
            where_clause = f"received_at > '{value}'"
    elif field == 'sender':
        if operator == 'contains':
            where_clause = f"lower(sender) LIKE '%{value}%'"
        elif operator == 'not_contains':
            where_clause = f"lower(sender) NOT LIKE '%{value}%'"
    elif field == 'subject':
        if operator == 'contains':
            where_clause = f"lower(subject) LIKE '%{value}%'"
        elif operator == 'not_contains':
            where_clause = f"lower(subject) NOT LIKE '%{value}%'"
    return where_clause

class Rule:
    def __init__(self, name, predicate, conditions, actions):
        self.name = name
        self.predicate = predicate
        self.conditions = conditions
        self.actions = actions


class RuleEngine:
    def __init__(self, rule_file_path: str):
        try:
            with open(rule_file_path, 'r') as f:
                rule_dicts = json.load(f)
        except Exception as e:
            raise Exception(f"Error while loading rule file: {e}")
        self.rules = [Rule(**r) for r in rule_dicts]
        self.executor = ActionExecutor()

    def fetch_emails_and_categorize(self):
        repo = EmailRepository()

        for rule in self.rules:
            # Create a base SQL query
            base_sql_query = 'select * from emails where '

            # Create a list of where clauses based on the conditions
            where_clause_list = []
            for condition in rule.conditions:
                where_clause_list.append(prepare_sql_query_based_on_rules(condition))

            if rule.predicate == 'AND':
                where_clause = ' and '.join(where_clause_list)
            elif rule.predicate == 'OR':
                where_clause = ' or '.join(where_clause_list)
            final_sql_query = base_sql_query + where_clause
            emails = repo.execute_sql_query(final_sql_query)

            for email in emails:
                self.executor.categorize_actions(email, rule.actions)

    def process(self, client):
        self.executor.execute(client)