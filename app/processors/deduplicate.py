import logging
from typing import List, Dict, Any, Optional
from processors.base import BaseProcessor

logger = logging.getLogger(__name__)


class DeduplicationProcessor(BaseProcessor):
    """Processor for deduplicating host data based on IP address."""

    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate hosts based on (ip, hostname) and return unique hosts."""
        if not data:
            logger.info("📭 No data to deduplicate")
            return []

        logger.info("🧠 Starting deduplication of %d hosts", len(data))

        seen_keys: set[tuple[Any, ...]] = set()
        unique_hosts: List[Dict[str, Any]] = []
        duplicates_count = 0
        duplicates: list = []

        for host in data:
            ip = host.get("ip")
            hostname = host.get("hostname")
            key: Optional[tuple[Any, ...]]
            if ip and hostname:
                key = (ip, hostname)
            elif ip:
                key = (ip,)
            elif hostname:
                key = (hostname,)
            else:
                key = None

            if key is not None and key not in seen_keys:
                seen_keys.add(key)
                unique_hosts.append(host)
            elif key is None:
                logger.warning("⚠️ Host without IP and hostname: %s", host)
                unique_hosts.append(host)
            else:
                duplicates_count += 1
                duplicates.append(key)
                logger.debug(
                    "🔄 Duplicate host found: %s (%s)",
                    host.get("hostname", "Unknown"),
                    ip,
                )

        logger.info(
            "✅ Deduplication completed: %d -> %d hosts (%d duplicates removed)",
            len(data),
            len(unique_hosts),
            duplicates_count,
        )

        if duplicates:
            logger.info("🔑 Duplicate keys: %s", duplicates)

        return unique_hosts
