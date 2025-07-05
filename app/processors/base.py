from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseProcessor(ABC):
    @abstractmethod
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process data and return processed data"""
