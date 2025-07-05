import logging
from typing import List, Dict, Any
from pipeline.config import PipelineConfig

logger = logging.getLogger(__name__)


class HostProcessingPipeline:
    """ETL pipeline for processing and deduplicating host data from multiple sources."""

    def __init__(self, config: PipelineConfig) -> None:
        """Initialize HostProcessingPipeline with configuration."""
        self.fetchers = config.fetchers
        self.normalizer = config.normalizer
        self.deduplicator = config.deduplicator
        self.storage = config.storage
        self.visualizer = config.visualizer

    def run(self) -> None:
        """Execute the complete ETL pipeline with deduplication."""
        logger.info("🔄 Starting Host Processing Pipeline")

        # Extract
        logger.info("[📥 EXTRACT]: Fetching data from all sources")
        all_hosts = self._extract()
        logger.info("[📥 EXTRACT]: Completed - %d hosts fetched", len(all_hosts))

        # Transform
        logger.info("[🔄 TRANSFORM]: Normalizing and deduplicating hosts")
        unique_hosts = self._transform(all_hosts)
        logger.info("[🔄 TRANSFORM]: Completed - %d unique hosts", len(unique_hosts))

        # Load
        logger.info("[💾 LOAD]: Storing data to MongoDB")
        self._load(unique_hosts)
        logger.info("[💾 LOAD]: Completed - Data stored successfully")

        # Visualize
        logger.info("[📊 VISUALIZE]: Generating charts and statistics")
        self._visualize(unique_hosts)
        logger.info("[📊 VISUALIZE]: Completed - Charts generated")

    def _extract(self) -> List[Dict[str, Any]]:
        """Extract data from all sources."""
        all_hosts = []
        for fetcher in self.fetchers:
            logger.info("📡 Fetching data from %s", fetcher)
            hosts = fetcher.fetch()
            all_hosts.extend(hosts)
            logger.debug("📡 Fetched %d hosts from %s", len(hosts), fetcher)
        return all_hosts

    def _transform(self, hosts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform and deduplicate hosts."""
        logger.info("🧹 Normalizing host data")
        normalized_hosts = self.normalizer.process(hosts)

        logger.info("🧠 Deduplicating hosts")
        unique_hosts = self.deduplicator.process(normalized_hosts)
        return unique_hosts

    def _load(self, hosts: List[Dict[str, Any]]) -> None:
        """Load data to storage."""
        logger.info("💾 Storing %d hosts to MongoDB", len(hosts))
        self.storage.save(hosts)

    def _visualize(self, hosts: List[Dict[str, Any]]) -> None:
        """Generate visualizations."""
        logger.info("📊 Generating charts and statistics")
        stats = self.visualizer.generate()
        logger.info("📊 Generated stats: %s", stats)
