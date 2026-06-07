"""Tests for package-level imports."""


class TestPackageImport:
    """Tests for package-level import."""

    def test_public_api(self) -> None:
        import pipette

        expected = [
            "NA_STRINGS",
            "PIPETTE_TESTS_URL",
            "atomize",
            "cache_url",
            "decode",
            "droplevels",
            "encode",
            "export_data",
            "factorize",
            "fill_lines",
            "get_json",
            "get_url_dir_list",
            "import_data",
            "init_dir",
            "load_data",
            "load_remote_data",
            "match_rowname_column",
            "md5",
            "metadata2",
            "na_strings",
            "paste_url",
            "remove_na",
            "sanitize_na",
            "sanitize_percent",
            "save_data",
            "sha256",
            "transmit",
            "unfactorize",
        ]
        for name in expected:
            assert hasattr(pipette, name), f"Missing: {name}"
