#!/usr/bin/env python3
"""Main ETL pipeline for processing host data from multiple sources."""

import logging
import time
from dotenv import load_dotenv
from fetchers.qualys import QualysFetcher
from fetchers.crowdstrike import CrowdstrikeFetcher
from processors.normalize import HostNormalizer
from processors.deduplicate import DeduplicationProcessor
from storage.mongo import MongoStorage
from visualizations.charts import ChartsVisualizer
from pipeline.host_processing_pipeline import HostProcessingPipeline
from pipeline.config import PipelineConfig

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("etl_pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

load_dotenv()


def main() -> None:
    """Main ETL pipeline execution."""
    start_time = time.time()
    logger.info("🚀 Starting Host Processing Pipeline")

    try:
        # Initialize components
        logger.info("🔧 Initializing pipeline components")
        fetchers = [QualysFetcher(), CrowdstrikeFetcher()]
        normalizer = HostNormalizer()
        deduplicator = DeduplicationProcessor()
        storage = MongoStorage()
        visualizer = ChartsVisualizer()

        # Create and run pipeline
        logger.info("🏗️ Creating Host Processing Pipeline")
        config = PipelineConfig(
            fetchers=fetchers,
            normalizer=normalizer,
            deduplicator=deduplicator,
            storage=storage,
            visualizer=visualizer,
        )
        pipeline = HostProcessingPipeline(config)

        # Run pipeline
        logger.info("▶️ Executing Host Processing Pipeline")
        pipeline.run()

        # Calculate execution time
        execution_time = time.time() - start_time

        # Log success with metrics
        logger.info(
            "✅ Pipeline completed successfully",
            extra={
                "execution_time_seconds": round(execution_time, 2),
                "fetchers_count": len(fetchers),
                "status": "success",
            },
        )

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(
            "❌ Pipeline failed: %s",
            e,
            extra={
                "execution_time_seconds": round(execution_time, 2),
                "error_type": type(e).__name__,
                "status": "failed",
            },
        )
        raise


if __name__ == "__main__":
    main()
