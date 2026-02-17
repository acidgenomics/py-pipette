"""Tests for package-level imports."""



class TestPackageImport:
    """Tests for package-level import."""

    def test_import(self) -> None:
        import pipette

        assert hasattr(pipette, "__version__")
        assert pipette.__version__ == "0.15.3"

    def test_public_api(self) -> None:
        import pipette

        expected = [
            "import_data",
            "export_data",
            "load_data",
            "save_data",
            "sanitize_na",
            "sanitize_percent",
            "remove_na",
            "factorize",
            "unfactorize",
            "atomize",
            "match_rowname_column",
            "metadata2",
            "md5",
            "sha256",
            "fill_lines",
            "get_json",
            "get_url_dir_list",
            "cache_url",
            "transmit",
            "load_remote_data",
            "na_strings",
            "NA_STRINGS",
        ]
        for name in expected:
            assert hasattr(pipette, name), f"Missing: {name}"
