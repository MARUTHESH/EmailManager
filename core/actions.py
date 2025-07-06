from collections import defaultdict
from core.models import Email

class ActionExecutor:
    def __init__(self):
        self.mark_as_unread_email_ids = []
        self.mark_read_email_ids = []
        self.move_to_folder_email_ids = defaultdict(list)

    # def execute(self, email: Email, actions, client):
    def categorize_actions(self, email: Email, actions):
        for action in actions:
            action_type = action.get('type', '').lower()
            if not action_type:
                raise ValueError(f"Action type not found for {action}")

            if action_type == 'mark_unread':
                self.mark_as_unread_email_ids.append(email.id)
            elif action_type == 'mark_read':
                self.mark_read_email_ids.append(email.id)
            elif action_type == 'move_to':
                folder = action['folder']
                self.move_to_folder_email_ids[folder].append(email.id)


    def execute(self, client):
        if self.mark_as_unread_email_ids:
            client.mark_as_unread(self.mark_as_unread_email_ids)
        if self.mark_read_email_ids:
            client.mark_as_read(self.mark_read_email_ids)
        if self.move_to_folder_email_ids:
            client.move_to_folder(self.move_to_folder_email_ids)