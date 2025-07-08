import os
import logging
from typing import List, Dict, Any
from pymongo import MongoClient, ASCENDING, UpdateOne
from pymongo.errors import OperationFailure
from storage.base import BaseStorage

logger = logging.getLogger(__name__)
client: MongoClient = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017"))
db = client["hosts_db"]
collection = db["hosts"]


class MongoStorage(BaseStorage):
    def save(self, data: List[Dict[str, Any]], batch_size: int = 1000) -> None:
        """
        Save data to MongoDB in batches using bulk_write.
        Args:
            data: List of host dicts.
            batch_size: Number of records per batch.
        """
        if not data:
            logger.info("📭 No data to save")
            return

        logger.info("💾 Saving %d hosts to MongoDB", len(data))

        # Create index if it doesn't exist
        try:
            collection.create_index(
                [("ip", ASCENDING), ("hostname", ASCENDING)], unique=True
            )
            logger.info("🔧 Created/verified MongoDB index")
        except OperationFailure as e:
            logger.warning("⚠️ Could not create index: %s", e)

        saved_count = 0

        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            operations = []
            for host in batch:
                operations.append(
                    UpdateOne(
                        {"ip": host["ip"], "hostname": host["hostname"]},
                        {"$set": host},
                        upsert=True,
                    )
                )
            try:
                result = collection.bulk_write(operations, ordered=False)
                saved_count += result.upserted_count + result.modified_count
                logger.info(
                    "💾 Batch %d-%d: %d upserted, %d modified",
                    i + 1,
                    i + len(batch),
                    result.upserted_count,
                    result.modified_count,
                )
            except (OperationFailure, ValueError) as e:
                logger.error(
                    "❌ Error saving batch %d-%d: %s",
                    i + 1,
                    i + len(batch),
                    e,
                )

        logger.info("✅ Successfully processed %d hosts to MongoDB", saved_count)
