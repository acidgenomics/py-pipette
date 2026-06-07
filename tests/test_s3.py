"""Tests for S3 utilities."""

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

from pipette._s3 import _is_s3_uri, _s3_download, _s3_parse_uri, _s3_upload


def _make_boto3_mock() -> tuple[ModuleType, MagicMock]:
    """Create a fake boto3 module with a mock client."""
    mock_client = MagicMock()
    boto3_mock = ModuleType("boto3")
    boto3_mock.client = MagicMock(return_value=mock_client)  # type: ignore[attr-defined]
    return boto3_mock, mock_client


class TestIsS3Uri:
    """Tests for _is_s3_uri()."""

    def test_s3_uri(self) -> None:
        assert _is_s3_uri("s3://bucket/key") is True

    def test_local_path(self) -> None:
        assert _is_s3_uri("/tmp/file.csv") is False

    def test_https_url(self) -> None:
        assert _is_s3_uri("https://example.com/file.csv") is False

    def test_partial_match(self) -> None:
        assert _is_s3_uri("s3:/bucket") is False


class TestS3ParseUri:
    """Tests for _s3_parse_uri()."""

    def test_basic(self) -> None:
        bucket, key = _s3_parse_uri("s3://my-bucket/path/to/file.csv")
        assert bucket == "my-bucket"
        assert key == "path/to/file.csv"

    def test_top_level_key(self) -> None:
        bucket, key = _s3_parse_uri("s3://my-bucket/file.csv")
        assert bucket == "my-bucket"
        assert key == "file.csv"


class TestS3Download:
    """Tests for _s3_download() with mocked boto3."""

    def test_downloads_to_temp_file(self) -> None:
        boto3_mock, mock_client = _make_boto3_mock()
        with patch.dict(sys.modules, {"boto3": boto3_mock}):
            path = _s3_download("s3://bucket/data.csv", quiet=True)
        assert path.endswith(".csv")
        mock_client.download_file.assert_called_once_with("bucket", "data.csv", path)

    def test_raises_without_boto3(self) -> None:
        with (
            patch.dict("sys.modules", {"boto3": None}),
            pytest.raises(ImportError, match="boto3 is required"),
        ):
            _s3_download("s3://bucket/file.csv", quiet=True)


class TestS3Upload:
    """Tests for _s3_upload() with mocked boto3."""

    def test_uploads_file(self, tmp_path) -> None:
        local = tmp_path / "file.csv"
        local.write_text("a,b\n1,2\n")
        boto3_mock, mock_client = _make_boto3_mock()
        with patch.dict(sys.modules, {"boto3": boto3_mock}):
            result = _s3_upload(str(local), "s3://bucket/file.csv", quiet=True)
        assert result == "s3://bucket/file.csv"
        mock_client.upload_file.assert_called_once_with(str(local), "bucket", "file.csv")

    def test_raises_without_boto3(self, tmp_path) -> None:
        local = tmp_path / "file.csv"
        local.write_text("data")
        with (
            patch.dict("sys.modules", {"boto3": None}),
            pytest.raises(ImportError, match="boto3 is required"),
        ):
            _s3_upload(str(local), "s3://bucket/file.csv", quiet=True)
