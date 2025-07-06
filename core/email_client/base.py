from typing import List
from abc import ABC, abstractmethod
from core.models import Email

class EmailClient(ABC):

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def fetch_emails(self) -> List[Email]:
        pass
