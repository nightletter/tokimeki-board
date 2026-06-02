from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

from src.services.update_checker import UpdateChecker, UpdateCheckResult


class TestUpdateChecker:
    """Test UpdateChecker version comparison and API calls."""

    def test_compare_versions_current_is_older(self):
        """Test that newer version is detected correctly."""
        assert UpdateChecker._compare_versions("0.2.0", "0.1.0") is True
        assert UpdateChecker._compare_versions("1.0.0", "0.9.0") is True
        assert UpdateChecker._compare_versions("0.1.1", "0.1.0") is True

    def test_compare_versions_current_is_newer(self):
        """Test that older version is not flagged as update."""
        assert UpdateChecker._compare_versions("0.1.0", "0.2.0") is False
        assert UpdateChecker._compare_versions("0.9.0", "1.0.0") is False
        assert UpdateChecker._compare_versions("0.1.0", "0.1.1") is False

    def test_compare_versions_equal(self):
        """Test that equal versions are not flagged as update."""
        assert UpdateChecker._compare_versions("0.1.0", "0.1.0") is False
        assert UpdateChecker._compare_versions("1.0.0", "1.0.0") is False

    def test_compare_versions_different_lengths(self):
        """Test version comparison with different lengths."""
        assert UpdateChecker._compare_versions("1.0", "0.9.9") is True
        assert UpdateChecker._compare_versions("0.1.0.1", "0.1.0") is True
        assert UpdateChecker._compare_versions("0.1.0", "0.1.0.1") is False

    def test_compare_versions_invalid_format(self):
        """Test that invalid version formats return False."""
        assert UpdateChecker._compare_versions("invalid", "0.1.0") is False
        assert UpdateChecker._compare_versions("0.1.0", "invalid") is False
        assert UpdateChecker._compare_versions(None, "0.1.0") is False

    @patch("src.services.update_checker.requests")
    def test_check_for_updates_new_version_available(self, mock_requests):
        """Test successful update check with new version."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tag_name": "v0.2.0",
            "html_url": "https://github.com/nightletter/tokimeki-board/releases/tag/v0.2.0",
        }
        mock_requests.get.return_value = mock_response

        checker = UpdateChecker("0.1.0")
        result = checker.check_for_updates()

        assert result.has_update is True
        assert result.latest_version == "0.2.0"
        assert result.current_version == "0.1.0"
        assert result.download_url == "https://github.com/nightletter/tokimeki-board/releases/tag/v0.2.0"

    @patch("src.services.update_checker.requests")
    def test_check_for_updates_no_new_version(self, mock_requests):
        """Test successful update check with no new version."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tag_name": "v0.1.0",
            "html_url": "https://github.com/nightletter/tokimeki-board/releases/tag/v0.1.0",
        }
        mock_requests.get.return_value = mock_response

        checker = UpdateChecker("0.1.0")
        result = checker.check_for_updates()

        assert result.has_update is False
        assert result.latest_version is None

    @patch("src.services.update_checker.requests")
    def test_check_for_updates_network_error(self, mock_requests):
        """Test update check with network error."""
        import src.services.update_checker
        mock_requests.get.side_effect = src.services.update_checker.RequestException("Network error")

        checker = UpdateChecker("0.1.0")
        with patch.object(checker, "_fetch_with_urllib", return_value=None):
            result = checker.check_for_updates()

        assert result.has_update is False
        assert result.current_version == "0.1.0"

    def test_check_for_updates_no_requests_library(self):
        """Test update check when requests library is not available."""
        checker = UpdateChecker("0.1.0")
        # Temporarily mock requests as None
        original_requests = __import__("src.services.update_checker", fromlist=["requests"]).requests
        try:
            import src.services.update_checker
            src.services.update_checker.requests = None
            with patch.object(checker, "_fetch_with_urllib", return_value=None):
                result = checker.check_for_updates()
            assert result.has_update is False
        finally:
            src.services.update_checker.requests = original_requests

    @patch("src.services.update_checker.requests")
    def test_check_for_updates_falls_back_to_urllib(self, mock_requests):
        """Test fallback path when requests call fails."""
        import src.services.update_checker
        mock_requests.get.side_effect = src.services.update_checker.RequestException("requests failed")
        checker = UpdateChecker("0.1.0")
        with patch.object(
            checker,
            "_fetch_with_urllib",
            return_value={
                "tag_name": "v0.2.0",
                "html_url": "https://github.com/nightletter/tokimeki-board/releases/tag/v0.2.0",
            },
        ):
            result = checker.check_for_updates()

        assert result.has_update is True
        assert result.latest_version == "0.2.0"

    @patch("src.services.update_checker.requests")
    def test_check_for_updates_async(self, mock_requests):
        """Test asynchronous update check."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tag_name": "v0.2.0",
            "html_url": "https://github.com/nightletter/tokimeki-board/releases/tag/v0.2.0",
        }
        mock_requests.get.return_value = mock_response

        checker = UpdateChecker("0.1.0")
        callback_result = []

        def callback(result):
            callback_result.append(result)

        checker.check_for_updates_async(callback)

        # Wait for async operation
        import time
        time.sleep(0.5)

        assert len(callback_result) == 1
        assert callback_result[0].has_update is True
        assert callback_result[0].latest_version == "0.2.0"

    @patch("src.services.update_checker.requests")
    def test_check_for_updates_empty_tag_name(self, mock_requests):
        """Test update check with empty tag name in response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tag_name": "",
            "html_url": "https://example.com",
        }
        mock_requests.get.return_value = mock_response

        checker = UpdateChecker("0.1.0")
        result = checker.check_for_updates()

        assert result.has_update is False
