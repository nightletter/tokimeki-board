from __future__ import annotations

import threading
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal

try:
    import requests
except ImportError:
    requests = None


@dataclass(frozen=True)
class UpdateCheckResult:
    has_update: bool
    current_version: str
    latest_version: str | None = None
    download_url: str | None = None


class UpdateChecker(QObject):
    update_result = pyqtSignal(object)
    GITHUB_API_URL = "https://api.github.com/repos/nightletter/tokimeki-board/releases/latest"
    
    def __init__(self, current_version: str):
        super().__init__()
        self.current_version = current_version

    def check_for_updates(self) -> UpdateCheckResult:
        if requests is None:
            return UpdateCheckResult(has_update=False, current_version=self.current_version)
        
        try:
            response = requests.get(self.GITHUB_API_URL, timeout=5)
            response.raise_for_status()
            release_data = response.json()
            
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
        except Exception:
            pass
        
        return UpdateCheckResult(has_update=False, current_version=self.current_version)
    
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
