"""Host normalization processor."""

from typing import List, Dict, Any
from processors.base import BaseProcessor


class HostNormalizer(BaseProcessor):
    """Normalizes host data from different sources to unified format."""

    @staticmethod
    def normalize_hosts(
        qualys_data: List[Dict[str, Any]], crowdstrike_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Normalize Qualys and Crowdstrike data to unified host format.
        Args:
            qualys_data: List of Qualys host dicts.
            crowdstrike_data: List of Crowdstrike host dicts.
        Returns:
            List of normalized host dicts.
        """
        normalized: List[Dict[str, Any]] = []

        for item in qualys_data:
            normalized.append(
                {
                    "source": "qualys",
                    "hostname": item.get("name") or item.get("hostname"),
                    "ip": item.get("address") or item.get("ip"),
                    "os": item.get("os"),
                    "last_seen": item.get("modified") or item.get("lastSeen"),
                }
            )

        for item in crowdstrike_data:
            normalized.append(
                {
                    "source": "crowdstrike",
                    "hostname": item.get("hostname"),
                    "ip": item.get("local_ip") or item.get("ip"),
                    "os": item.get("platform_name") or item.get("os"),
                    "last_seen": (item.get("last_seen") or item.get("lastSeenDate")),
                }
            )

        return normalized

    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process raw data from multiple sources and normalize it.
        Args:
            data: List of raw host dicts.
        Returns:
            List of normalized host dicts.
        """
        qualys_data: List[Dict[str, Any]] = []
        crowdstrike_data: List[Dict[str, Any]] = []

        for item in data:
            if "source" in item:
                if item["source"] == "qualys":
                    qualys_data.append(item)
                elif item["source"] == "crowdstrike":
                    crowdstrike_data.append(item)
            else:
                if "platform_name" in item or "platform_id" in item:
                    crowdstrike_data.append(item)
                else:
                    qualys_data.append(item)

        return self.normalize_hosts(qualys_data, crowdstrike_data)
