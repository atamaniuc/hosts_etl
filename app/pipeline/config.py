from dataclasses import dataclass
from typing import List
from fetchers.base import BaseFetcher
from processors.normalize import HostNormalizer
from processors.deduplicate import DeduplicationProcessor
from storage.mongo import MongoStorage
from visualizations.charts import ChartsVisualizer


@dataclass
class PipelineConfig:
    """Configuration class for HostProcessingPipeline components."""

    fetchers: List[BaseFetcher]
    normalizer: HostNormalizer
    deduplicator: DeduplicationProcessor
    storage: MongoStorage
    visualizer: ChartsVisualizer
