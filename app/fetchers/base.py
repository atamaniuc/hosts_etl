import os
import logging
from abc import ABC
from typing import List, Dict, Any

import requests

logger = logging.getLogger(__name__)


class BaseFetcher(ABC):
    def __init__(self, base_url: str, source_name: str) -> None:
        self.base_url = base_url
        self.source_name = source_name
        self.page_size = 2  # Use 2 for better performance
        self.api_token = os.getenv("API_TOKEN")

    def __str__(self) -> str:
        """Return a human-readable representation of the fetcher"""
        return self.__class__.__name__

    def _handle_api_error(self, response, skip: int) -> tuple[bool, list]:
        """Handle API error responses and return (should_break, hosts_to_add)."""
        error_text = response.text.lower()
        if "invalid skip/limit combo" in error_text or ">number of hosts" in error_text:
            logger.debug(
                "🔄 API returned pagination end for %s, "
                "trying final page with limit=1",
                self.source_name,
            )
            # Try with page_size=1 for the last host
            if self.page_size == 2:
                params = {"skip": skip, "limit": 1}
                headers = {"token": self.api_token, "accept": "application/json"}
                response = requests.post(
                    self.base_url,
                    params=params,
                    headers=headers,
                    data="",
                    timeout=30,
                )
                if response.status_code == 200:
                    hosts = response.json()
                    if hosts:
                        logger.debug(
                            "✅ Retrieved final host from %s", self.source_name
                        )
                        for host in hosts:
                            host["source"] = self.source_name
                        return True, hosts
            return True, []

        # Other 500 error - raise it
        logger.error(
            "❌ API error from %s: %d - %s",
            self.source_name,
            response.status_code,
            response.text,
        )
        response.raise_for_status()
        return False, []

    def fetch(self) -> List[Dict[str, Any]]:
        """Fetch data from the API with hybrid pagination strategy"""
        if not self.api_token:
            logger.error("❌ API_TOKEN not set in environment variables")
            raise ValueError("API_TOKEN not set in environment variables")

        logger.info("📡 Starting data fetch from %s", self.source_name)
        headers = {"token": self.api_token, "accept": "application/json"}
        all_hosts: List[Dict[str, Any]] = []
        skip = 0
        page_count = 0

        while True:
            page_count += 1
            # Use page_size=2 for most requests, but page_size=1 for last page
            params = {"skip": skip, "limit": self.page_size}
            try:
                logger.debug(
                    "📄 Fetching page %d from %s (skip=%d, limit=%d)",
                    page_count,
                    self.source_name,
                    skip,
                    self.page_size,
                )
                response = requests.post(
                    self.base_url,
                    params=params,
                    headers=headers,
                    data="",
                    timeout=30,
                )

                # Handle specific API error for invalid skip/limit combo
                if response.status_code == 500:
                    logger.debug(
                        "🔄 Got 500 error from %s at skip=%d, limit=%d",
                        self.source_name,
                        skip,
                        self.page_size,
                    )
                    should_break, additional_hosts = self._handle_api_error(
                        response, skip
                    )
                    if additional_hosts:
                        all_hosts.extend(additional_hosts)
                    if should_break:
                        logger.debug(
                            "🔄 Breaking pagination loop for %s after error handling",
                            self.source_name,
                        )
                        break
                    continue

                response.raise_for_status()
                hosts = response.json()
                logger.debug(
                    "📥 Got %d hosts from %s (page %d, skip=%d, limit=%d)",
                    len(hosts),
                    self.source_name,
                    page_count,
                    skip,
                    self.page_size,
                )

                if not hosts:
                    logger.debug("📭 No more hosts from %s", self.source_name)
                    break

                for host in hosts:
                    host["source"] = self.source_name
                all_hosts.extend(hosts)

                if len(hosts) < self.page_size:
                    logger.debug(
                        "📭 Got fewer hosts than limit (%d < %d), ending pagination",
                        len(hosts),
                        self.page_size,
                    )
                    break
                skip += self.page_size

            except requests.exceptions.RequestException as e:
                logger.error("❌ Error fetching data from %s: %s", self.source_name, e)
                raise

        logger.info(
            "✅ Completed data fetch from %s: %d total hosts in %d pages",
            self.source_name,
            len(all_hosts),
            page_count,
        )
        return all_hosts
