from abc import ABC, abstractmethod
from typing import Any


class BaseVisualizer(ABC):
    @abstractmethod
    def generate(self) -> Any:
        """Generate visualizations"""
