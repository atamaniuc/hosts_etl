from fetchers.base import BaseFetcher

BASE_URL = "https://api.recruiting.app.silk.security/api"
CROWDSTRIKE_URL = f"{BASE_URL}/crowdstrike/hosts/get"


class CrowdstrikeFetcher(BaseFetcher):
    def __init__(self) -> None:
        super().__init__(CROWDSTRIKE_URL, "crowdstrike")
