"""Tests for pipette import functionality."""

import json
import pickle

import pandas as pd
import pytest

from pipette._import import _make_valid_names, import_data


@pytest.fixture
def example_csv(tmp_path):
    content = (
        "rowname,sample1,sample2,sample3,sample4\n"
        "gene1,16,20,13,16\n"
        "gene2,29,22,43,50\n"
        "gene3,243,245,186,184\n"
        "gene4,7,14,25,16\n"
        "gene5,1,1,2,2\n"
    )
    path = tmp_path / "example.csv"
    path.write_text(content)
    return str(path)


@pytest.fixture
def example_tsv(tmp_path):
    content = "rowname\tsample1\tsample2\ngene1\t16\t20\ngene2\t29\t22\n"
    path = tmp_path / "example.tsv"
    path.write_text(content)
    return str(path)


@pytest.fixture
def example_json(tmp_path):
    data = {"key1": "value1", "key2": [1, 2, 3]}
    path = tmp_path / "example.json"
    path.write_text(json.dumps(data))
    return str(path)


@pytest.fixture
def example_lines(tmp_path):
    content = "line1\nline2\nline3\n# comment\nline4\n"
    path = tmp_path / "example.log"
    path.write_text(content)
    return str(path)


class TestImportCSV:
    def test_basic_import(self, example_csv) -> None:
        df = import_data(example_csv, quiet=True)
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (5, 4)
        assert list(df.index) == ["gene1", "gene2", "gene3", "gene4", "gene5"]

    def test_import_no_rownames(self, example_csv) -> None:
        df = import_data(example_csv, rownames=False, quiet=True)
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (5, 5)
        assert "rowname" in df.columns

    def test_import_format_override(self, example_csv) -> None:
        df = import_data(example_csv, format="csv", quiet=True)
        assert isinstance(df, pd.DataFrame)


class TestImportTSV:
    def test_basic_import(self, example_tsv) -> None:
        df = import_data(example_tsv, quiet=True)
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (2, 2)
        assert list(df.index) == ["gene1", "gene2"]


class TestImportJSON:
    def test_basic_import(self, example_json) -> None:
        result = import_data(example_json, quiet=True)
        assert isinstance(result, dict)
        assert result["key1"] == "value1"


class TestImportLines:
    def test_basic_import(self, example_lines) -> None:
        result = import_data(example_lines, quiet=True)
        assert isinstance(result, list)
        assert "line1" in result

    def test_comment_filter(self, example_lines) -> None:
        result = import_data(example_lines, comment="#", quiet=True)
        assert "# comment" not in result


class TestImportGMT:
    def test_basic_gmt(self, tmp_path) -> None:
        content = (
            "PATHWAY1\tdescription1\tGENE1\tGENE2\tGENE3\nPATHWAY2\tdescription2\tGENE4\tGENE5\n"
        )
        path = tmp_path / "example.gmt"
        path.write_text(content)
        result = import_data(str(path), quiet=True)
        assert isinstance(result, dict)
        assert len(result) == 2
        assert result["PATHWAY1"] == ["GENE1", "GENE2", "GENE3"]


class TestImportPickle:
    def test_basic_pickle(self, tmp_path) -> None:
        data = {"key": "value", "numbers": [1, 2, 3]}
        path = tmp_path / "test.pickle"
        with open(str(path), "wb") as f:
            pickle.dump(data, f)
        result = import_data(str(path), quiet=True)
        assert result == data


class TestMakeValidNames:
    def test_spaces(self) -> None:
        assert _make_valid_names(["hello world"]) == ["hello_world"]

    def test_special_chars(self) -> None:
        assert _make_valid_names(["col-1"]) == ["col_1"]

    def test_leading_digit(self) -> None:
        assert _make_valid_names(["1col"]) == ["x1col"]

    def test_empty_string(self) -> None:
        assert _make_valid_names([""]) == ["x"]

    def test_unknown_format_error(self, tmp_path) -> None:
        path = tmp_path / "file"
        path.write_text("data")
        with pytest.raises(ValueError, match="Cannot detect format"):
            import_data(str(path), quiet=True)
