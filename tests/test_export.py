"""Tests for pipette export functionality."""

import json
import os

import pandas as pd
import pytest

from pipette._export import export_data
from pipette._import import import_data


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {"sample1": [16, 29, 243], "sample2": [20, 22, 245]},
        index=["gene1", "gene2", "gene3"],
    )


class TestExportCSV:
    def test_basic_export(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.csv")
        result = export_data(sample_df, path, quiet=True)
        assert os.path.isfile(result)
        imported = import_data(result, quiet=True)
        assert imported.shape == sample_df.shape

    def test_export_no_rownames(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.csv")
        export_data(sample_df, path, rownames=False, quiet=True)
        imported = import_data(path, rownames=False, quiet=True)
        assert "rowname" not in imported.columns


class TestExportTSV:
    def test_basic_export(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.tsv")
        result = export_data(sample_df, path, quiet=True)
        assert os.path.isfile(result)


class TestExportJSON:
    def test_dict_export(self, tmp_path) -> None:
        data = {"key1": "value1", "key2": [1, 2, 3]}
        path = str(tmp_path / "output.json")
        export_data(data, path, quiet=True)
        with open(path) as f:
            result = json.load(f)
        assert result == data


class TestExportPickle:
    def test_roundtrip(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.pickle")
        export_data(sample_df, path, quiet=True)
        imported = import_data(path, quiet=True)
        pd.testing.assert_frame_equal(imported, sample_df)


class TestExportLines:
    def test_list_export(self, tmp_path) -> None:
        data = ["line1", "line2", "line3"]
        path = str(tmp_path / "output.txt")
        export_data(data, path, quiet=True)
        with open(path) as f:
            content = f.read()
        assert content == "line1\nline2\nline3\n"


class TestExportCompressed:
    def test_gzip_export(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.csv.gz")
        result = export_data(sample_df, path, quiet=True)
        assert os.path.isfile(result)
        imported = import_data(result, quiet=True)
        assert imported.shape == sample_df.shape


class TestExportParquet:
    def test_roundtrip(self, sample_df, tmp_path) -> None:
        pytest.importorskip("pyarrow")
        path = str(tmp_path / "output.parquet")
        export_data(sample_df.reset_index(drop=True), path, quiet=True)
        imported = import_data(path, quiet=True)
        assert imported.shape == sample_df.shape


class TestExportFeather:
    def test_roundtrip(self, sample_df, tmp_path) -> None:
        pytest.importorskip("pyarrow")
        path = str(tmp_path / "output.feather")
        export_data(sample_df.reset_index(drop=True), path, quiet=True)
        imported = import_data(path, quiet=True)
        assert imported.shape == sample_df.shape


class TestExportExcel:
    def test_roundtrip(self, sample_df, tmp_path) -> None:
        pytest.importorskip("openpyxl")
        path = str(tmp_path / "output.xlsx")
        export_data(sample_df.reset_index(drop=True), path, quiet=True)
        imported = import_data(path, quiet=True)
        assert imported.shape == sample_df.shape


class TestExportOverwrite:
    def test_no_overwrite_by_default(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.csv")
        export_data(sample_df, path, quiet=True)
        with pytest.raises(FileExistsError):
            export_data(sample_df, path, overwrite=False, quiet=True)

    def test_overwrite_on_flag(self, sample_df, tmp_path) -> None:
        path = str(tmp_path / "output.csv")
        export_data(sample_df, path, quiet=True)
        export_data(sample_df, path, overwrite=True, quiet=True)
        assert os.path.isfile(path)
