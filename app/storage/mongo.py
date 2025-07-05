import os
import logging
from typing import List, Dict, Any
from pymongo import MongoClient, ASCENDING
from pymongo.errors import OperationFailure
from storage.base import BaseStorage

logger = logging.getLogger(__name__)
client: MongoClient = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017"))
db = client["hosts_db"]
collection = db["hosts"]


class MongoStorage(BaseStorage):
    def save(self, data: List[Dict[str, Any]]) -> None:
        """Save data to MongoDB"""
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
        for host in data:
            try:
                result = collection.update_one(
                    {"ip": host["ip"], "hostname": host["hostname"]},
                    {"$set": host},
                    upsert=True,
                )
                # Count both modified and upserted records
                if result.modified_count > 0 or result.upserted_id:
                    saved_count += 1
                    logger.info(
                        "💾 %s host: %s (%s)",
                        "Updated" if result.modified_count > 0 else "Created",
                        host.get("hostname", "Unknown"),
                        host.get("ip", "Unknown"),
                    )
                else:
                    logger.info(
                        "⏭️ Host already exists (no changes): %s (%s)",
                        host.get("hostname", "Unknown"),
                        host.get("ip", "Unknown"),
                    )
            except (OperationFailure, ValueError) as e:
                logger.error(
                    "❌ Error saving host %s: %s", host.get("hostname", "Unknown"), e
                )

        logger.info("✅ Successfully processed %d hosts to MongoDB", saved_count)
