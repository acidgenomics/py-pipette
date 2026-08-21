"""Tests for join_url."""

from pipette import join_url


class TestJoinUrl:
    """Tests for join_url()."""

    def test_basic_join(self) -> None:
        assert join_url("a", "b", "c") == "a/b/c"

    def test_strips_trailing_slashes(self) -> None:
        assert join_url("a/", "b/", "c/") == "a/b/c"

    def test_single_component(self) -> None:
        assert join_url("foo") == "foo"

    def test_protocol_https(self) -> None:
        assert join_url("example.com", "path", protocol="https") == "https://example.com/path"

    def test_protocol_s3(self) -> None:
        assert join_url("my-bucket", "key", protocol="s3") == "s3://my-bucket/key"

    def test_protocol_none_default(self) -> None:
        assert join_url("example.com", "path") == "example.com/path"

    def test_protocol_explicit_none(self) -> None:
        assert join_url("example.com", "path", protocol=None) == "example.com/path"

    def test_empty_args(self) -> None:
        assert join_url() == ""
