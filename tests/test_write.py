"""Tests for pipette write functionality."""

import json
import os
from pathlib import Path

import pandas as pd
import pytest

from pipette._read import read
from pipette._write import write


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {"sample1": [16, 29, 243], "sample2": [20, 22, 245]},
        index=["gene1", "gene2", "gene3"],
    )


class TestWriteCSV:
    def test_basic_write(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.csv")
        result = write(sample_df, path, quiet=True)
        assert isinstance(result, Path)
        assert result.is_file()
        loaded = read(result, quiet=True)
        assert loaded.shape == sample_df.shape

    def test_write_no_index(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.csv")
        write(sample_df, path, index=False, quiet=True)
        loaded = read(path, index=False, quiet=True)
        assert "rowname" not in loaded.columns

    def test_write_path_object(self, sample_df, tmp_path) -> None:
        path = tmp_path / "output.csv"
        result = write(sample_df, path, quiet=True)
        assert isinstance(result, Path)
        assert result.is_file()

    def test_write_forced_format(self, sample_df, tmp_path) -> None:
        path = tmp_path / "output.txt"
        result = write(sample_df, path, format="tsv", quiet=True)
        assert "\t" in result.read_text()


class TestWriteTSV:
    def test_basic_write(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.tsv")
        result = write(sample_df, path, quiet=True)
        assert os.path.isfile(result)


class TestWriteJSON:
    def test_dict_write(self, tmp_path) -> None:
        data = {"key1": "value1", "key2": [1, 2, 3]}
        path = str(tmp_path / "output.json")
        write(data, path, quiet=True)
        with open(path) as f:
            result = json.load(f)
        assert result == data


class TestWritePickle:
    def test_roundtrip(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.pickle")
        write(sample_df, path, quiet=True)
        loaded = read(path, quiet=True)
        pd.testing.assert_frame_equal(loaded, sample_df)


class TestWriteLines:
    def test_list_write(self, tmp_path) -> None:
        data = ["line1", "line2", "line3"]
        path = str(tmp_path / "output.txt")
        write(data, path, quiet=True)
        with open(path) as f:
            content = f.read()
        assert content == "line1\nline2\nline3\n"


class TestWriteCompressed:
    def test_gzip_write(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.csv.gz")
        result = write(sample_df, path, quiet=True)
        assert os.path.isfile(result)
        loaded = read(result, quiet=True)
        assert loaded.shape == sample_df.shape


class TestWriteParquet:
    def test_roundtrip(self, sample_df, tmp_path) -> None:
        pytest.importorskip("pyarrow")
        path = str(tmp_path / "output.parquet")
        write(sample_df.reset_index(drop=True), path, quiet=True)
        loaded = read(path, quiet=True)
        assert loaded.shape == sample_df.shape


class TestWriteFeather:
    def test_roundtrip(self, sample_df, tmp_path) -> None:
        pytest.importorskip("pyarrow")
        path = str(tmp_path / "output.feather")
        write(sample_df.reset_index(drop=True), path, quiet=True)
        loaded = read(path, quiet=True)
        assert loaded.shape == sample_df.shape


class TestWriteExcel:
    def test_roundtrip(self, sample_df, tmp_path) -> None:
        pytest.importorskip("openpyxl")
        path = str(tmp_path / "output.xlsx")
        write(sample_df.reset_index(drop=True), path, quiet=True)
        loaded = read(path, quiet=True)
        assert loaded.shape == sample_df.shape


class TestWriteOverwrite:
    def test_no_overwrite_by_default(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.csv")
        write(sample_df, path, quiet=True)
        with pytest.raises(FileExistsError):
            write(sample_df, path, overwrite=False, quiet=True)

    def test_overwrite_on_flag(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.csv")
        write(sample_df, path, quiet=True)
        write(sample_df, path, overwrite=True, quiet=True)
        assert os.path.isfile(path)
