"""Tests for utility functions."""

from pipette._file_utils import basename_sans_ext, compress_ext, file_ext, is_url
from pipette._fill_lines import fill_lines


class TestFillLines:
    def test_basic(self) -> None:
        lines = ["a,b,c", "d,e", "f"]
        result = fill_lines(lines, sep=",")
        assert result == ["a,b,c", "d,e,NA", "f,NA,NA"]

    def test_no_padding(self) -> None:
        lines = ["a,b", "c,d"]
        result = fill_lines(lines, sep=",")
        assert result == ["a,b", "c,d"]

    def test_empty_input(self) -> None:
        assert fill_lines([], sep=",") == []


class TestFileExt:
    def test_simple(self) -> None:
        assert file_ext("file.csv") == "csv"

    def test_compound(self) -> None:
        assert file_ext("file.csv.gz") == "csv.gz"

    def test_no_ext(self) -> None:
        assert file_ext("file") == ""

    def test_path(self) -> None:
        assert file_ext("/path/to/file.tsv") == "tsv"


class TestCompressExt:
    def test_gz(self) -> None:
        assert compress_ext("file.csv.gz") == "gz"

    def test_bz2(self) -> None:
        assert compress_ext("file.csv.bz2") == "bz2"

    def test_no_compression(self) -> None:
        assert compress_ext("file.csv") is None


class TestIsUrl:
    def test_http(self) -> None:
        assert is_url("http://example.com") is True

    def test_https(self) -> None:
        assert is_url("https://example.com") is True

    def test_ftp(self) -> None:
        assert is_url("ftp://example.com") is True

    def test_local(self) -> None:
        assert is_url("/path/to/file") is False


class TestBasenameSansExt:
    def test_simple(self) -> None:
        assert basename_sans_ext("file.csv") == "file"

    def test_path(self) -> None:
        assert basename_sans_ext("/path/to/file.csv") == "file"

    def test_compound(self) -> None:
        assert basename_sans_ext("file.csv.gz") == "file"

    def test_no_ext(self) -> None:
        assert basename_sans_ext("file") == "file"
