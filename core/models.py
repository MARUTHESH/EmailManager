from dataclasses import dataclass

@dataclass
class Email:
    id: str
    sender: str
    subject: str
    snippet: str
    received_at: str  # ISO timestamp (e.g. "2025-07-04T15:32:00Z")

