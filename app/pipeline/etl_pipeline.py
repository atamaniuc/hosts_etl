from abc import ABC, abstractmethod
from typing import List

from fetchers.base import BaseFetcher
from processors.base import BaseProcessor
from storage.base import BaseStorage
from visualizations.base import BaseVisualizer


class ETLPipeline(ABC):
    def __init__(
        self,
        fetchers: List[BaseFetcher],
        processor: BaseProcessor,
        storage: BaseStorage,
        visualizer: BaseVisualizer,
    ) -> None:
        self.fetchers = fetchers
        self.processor = processor
        self.storage = storage
        self.visualizer = visualizer

    @abstractmethod
    def run(self) -> None:
        """Run the ETL pipeline"""
