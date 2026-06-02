from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from PyQt6.QtCore import QObject, pyqtSignal

try:
    import requests
    from requests import RequestException
except ImportError:
    requests = None
    RequestException = Exception


@dataclass(frozen=True)
class UpdateCheckResult:
    has_update: bool
    current_version: str
    latest_version: str | None = None
    download_url: str | None = None


class UpdateChecker(QObject):
    update_result = pyqtSignal(object)
    GITHUB_API_URL = "https://api.github.com/repos/nightletter/tokimeki-board/releases/latest"
    REQUEST_HEADERS = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "tokimeki-board-update-checker",
    }
    
    def __init__(self, current_version: str):
        super().__init__()
        self.current_version = current_version

    def check_for_updates(self) -> UpdateCheckResult:
        release_data = self._fetch_latest_release_data()
        if release_data is None:
            return UpdateCheckResult(has_update=False, current_version=self.current_version)

        latest_version = release_data.get("tag_name", "").lstrip("v")
        if not latest_version:
            return UpdateCheckResult(has_update=False, current_version=self.current_version)

        if self._compare_versions(latest_version, self.current_version):
            return UpdateCheckResult(
                has_update=True,
                current_version=self.current_version,
                latest_version=latest_version,
                download_url=release_data.get("html_url"),
            )

        return UpdateCheckResult(has_update=False, current_version=self.current_version)

    def _fetch_latest_release_data(self) -> dict | None:
        if requests is not None:
            release_data = self._fetch_with_requests()
            if release_data is not None:
                return release_data
        return self._fetch_with_urllib()

    def _fetch_with_requests(self) -> dict | None:
        try:
            response = requests.get(self.GITHUB_API_URL, timeout=5, headers=self.REQUEST_HEADERS)
            response.raise_for_status()
            return response.json()
        except (RequestException, ValueError, TypeError):
            return None

    def _fetch_with_urllib(self) -> dict | None:
        request = Request(self.GITHUB_API_URL, headers=self.REQUEST_HEADERS)
        try:
            with urlopen(request, timeout=5) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError):
            return None
    
    def check_for_updates_async(self, callback: callable) -> None:
        def _check():
            result = self.check_for_updates()
            callback(result)
        
        thread = threading.Thread(target=_check, daemon=True)
        thread.start()

    # 버전 비교
    @staticmethod
    def _compare_versions(latest: str, current: str) -> bool:
        try:
            latest_parts = [int(x) for x in latest.split(".")]
            current_parts = [int(x) for x in current.split(".")]
            
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts += [0] * (max_len - len(latest_parts))
            current_parts += [0] * (max_len - len(current_parts))
            
            return latest_parts > current_parts
        except (ValueError, AttributeError):
            return False
