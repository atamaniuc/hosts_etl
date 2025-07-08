import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any
import matplotlib.pyplot as plt

from pymongo import MongoClient

from visualizations.base import BaseVisualizer

client: MongoClient = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017"))
db = client["hosts_db"]
collection = db["hosts"]

# Define the base directory for storing images
# Using Path to handle directory structure correctly regardless of OS
IMAGES_DIR = Path("visualizations/images")


class ChartsVisualizer(BaseVisualizer):
    def normalize_os_name(self, os_name: str) -> str:
        """Normalize OS names for better chart display"""
        if not os_name:
            return "Unknown"

        os_name = os_name.lower()

        # OS mapping dictionary to reduce return statements
        os_mapping = {
            "amazon linux": "Linux",
            "linux": "Linux",
            "windows": "Windows",
            "mac": "macOS",
            "darwin": "macOS",
            "ubuntu": "Ubuntu",
            "centos": "CentOS",
            "red hat": "Red Hat",
            "rhel": "Red Hat",
        }

        for os_key, normalized_name in os_mapping.items():
            if os_key in os_name:
                return normalized_name

        return "Other"

    def generate(self) -> Dict[str, Any]:
        """Generate charts and statistics"""
        hosts = list(collection.find({}, {"_id": 0}))

        # Count by source
        source_counts: Dict[str, int] = {}
        for host in hosts:
            source = host.get("source", "unknown")
            source_counts[source] = source_counts.get(source, 0) + 1

        # Count by OS (with normalization)
        os_counts: Dict[str, int] = {}
        for host in hosts:
            os_name = host.get("os", "unknown")
            normalized_os = self.normalize_os_name(os_name)
            os_counts[normalized_os] = os_counts.get(normalized_os, 0) + 1

        # Count old hosts (not seen in 30 days)
        threshold = datetime.now() - timedelta(days=30)
        old = 0
        recent = 0
        for host in hosts:
            if "last_seen" in host and host["last_seen"]:
                try:
                    seen = datetime.strptime(host["last_seen"], "%Y-%m-%dT%H:%M:%S")
                    if seen < threshold:
                        old += 1
                    else:
                        recent += 1
                except ValueError:
                    old += 1
            else:
                old += 1

        # Create visualizations
        self._create_os_distribution_chart(os_counts)
        self._create_host_freshness_chart(old, recent)
        self._create_source_distribution_chart(source_counts)

        return {
            "total_hosts": len(hosts),
            "by_source": source_counts,
            "by_os": os_counts,
            "old_hosts": old,
            "recent_hosts": recent,
        }

    def _create_os_distribution_chart(self, os_counts: Dict[str, int]) -> None:
        """Create OS distribution pie chart"""
        if not os_counts:
            return

        plt.figure(figsize=(10, 8))
        plt.pie(
            list(os_counts.values()),
            labels=list(os_counts.keys()),
            autopct="%1.1f%%",
            startangle=90,
        )
        plt.title("Host OS Distribution", fontsize=16, fontweight="bold")
        plt.axis("equal")

        # Ensure directory exists
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        plt.savefig(
            IMAGES_DIR / "os_distribution.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    def _create_host_freshness_chart(self, old: int, recent: int) -> None:
        """Create host freshness pie chart"""
        if old == 0 and recent == 0:
            return

        plt.figure(figsize=(10, 8))
        labels = ["Old Hosts (>30 days)", "Recent Hosts (≤30 days)"]
        sizes = [old, recent]
        colors = ["#ff9999", "#66b3ff"]

        plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        plt.title("Host Freshness Distribution", fontsize=16, fontweight="bold")
        plt.axis("equal")

        # Ensure directory exists
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        plt.savefig(IMAGES_DIR / "host_age_pie.png", dpi=300, bbox_inches="tight")
        plt.close()

    def _create_source_distribution_chart(self, source_counts: Dict[str, int]) -> None:
        """Create source distribution pie chart"""
        plt.figure(figsize=(10, 8))
        labels = list(source_counts.keys())
        sizes = list(source_counts.values())
        colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#feca57"]

        plt.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        plt.title("Host Distribution by Source", fontsize=16, fontweight="bold")
        plt.axis("equal")

        # Ensure directory exists
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        plt.savefig(
            IMAGES_DIR / "source_distribution.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()
