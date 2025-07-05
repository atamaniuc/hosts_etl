from fetchers.base import BaseFetcher

BASE_URL = "https://api.recruiting.app.silk.security/api"
QUALYS_URL = f"{BASE_URL}/qualys/hosts/get"


class QualysFetcher(BaseFetcher):
    def __init__(self) -> None:
        super().__init__(QUALYS_URL, "qualys")
