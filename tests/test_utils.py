"""Tests for utility functions."""

from pipette._checksums import md5, sha256
from pipette._file_utils import basename_sans_ext, compress_ext, file_ext, is_url
from pipette._fill_lines import fill_lines


class TestMd5:
    def test_basic(self, tmp_path) -> None:
        path = tmp_path / "test.txt"
        path.write_text("hello world\n")
        result = md5(str(path))
        assert isinstance(result, str)
        assert len(result) == 32

    def test_deterministic(self, tmp_path) -> None:
        path = tmp_path / "test.txt"
        path.write_text("hello")
        assert md5(str(path)) == md5(str(path))


class TestSha256:
    def test_basic(self, tmp_path) -> None:
        path = tmp_path / "test.txt"
        path.write_text("hello world\n")
        result = sha256(str(path))
        assert isinstance(result, str)
        assert len(result) == 64

    def test_different_content(self, tmp_path) -> None:
        f1 = tmp_path / "f1.txt"
        f2 = tmp_path / "f2.txt"
        f1.write_text("content1")
        f2.write_text("content2")
        assert sha256(str(f1)) != sha256(str(f2))


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
