from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseStorage(ABC):
    @abstractmethod
    def save(self, data: List[Dict[str, Any]]) -> None:
        """Save data to storage"""
