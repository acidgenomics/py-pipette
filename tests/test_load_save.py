"""Tests for save_data and load_data."""

import os

import pandas as pd
import pytest

from pipette._load_data import load_data
from pipette._save_data import save_data


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {"sample1": [16, 29, 243], "sample2": [20, 22, 245]},
        index=["gene1", "gene2", "gene3"],
    )


class TestSaveData:
    def test_csv(self, sample_df, tmp_path) -> None:
        result = save_data(
            sample_df,
            name="test_data",
            dir=str(tmp_path),
            ext="csv",
            quiet=True,
        )
        assert os.path.isfile(result)

    def test_pickle(self, sample_df, tmp_path) -> None:
        result = save_data(
            sample_df,
            name="test_data",
            dir=str(tmp_path),
            ext="pickle",
            quiet=True,
        )
        assert os.path.isfile(result)


class TestLoadData:
    def test_csv(self, sample_df, tmp_path) -> None:
        save_data(
            sample_df,
            name="test_data",
            dir=str(tmp_path),
            ext="csv",
            quiet=True,
        )
        result = load_data("test_data", dir=str(tmp_path), quiet=True)
        assert isinstance(result, pd.DataFrame)
        assert result.shape == sample_df.shape

    def test_missing(self, tmp_path) -> None:
        with pytest.raises(FileNotFoundError):
            load_data("nonexistent", dir=str(tmp_path), quiet=True)
