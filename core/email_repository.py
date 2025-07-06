import sqlite3
from typing import List
from core.models import Email


class EmailRepository:
    _instance = None
    _conn = None

    def __new__(cls, db_path='emails.db'):
        if cls._instance is None:
            cls._instance = super(EmailRepository, cls).__new__(cls)
            cls._instance._initialize_db(db_path)
        return cls._instance

    def _initialize_db(self, db_path):
        if self._conn is None:
            self._conn = sqlite3.connect(db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._create_table()

    def _create_table(self):
        self._conn.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                sender TEXT,
                subject TEXT,
                snippet TEXT,
                received_at TEXT
            )
        ''')
        self._conn.commit()

    def save_emails(self, emails: List[Email]):
        with self._conn:
            for email in emails:
                self._conn.execute(
                    'INSERT OR IGNORE INTO emails (id, sender, subject, snippet, received_at) VALUES (?, ?, ?, ?, ?)',
                    (email.id, email.sender, email.subject, email.snippet, email.received_at)
                )

    def execute_sql_query(self, sql_query: str):
        with self._conn:
            cursor = self._conn.execute(sql_query)
            return [Email(**dict(row)) for row in cursor.fetchall()]

    def close_connection(self):
        """Close the database connection. Use with caution as this affects all instances."""
        if self._conn:
            self._conn.close()
            self._conn = None