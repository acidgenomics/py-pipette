"""Tests for package-level imports."""


class TestPackageImport:
    """Tests for package-level import."""

    def test_public_api(self) -> None:
        import pipette

        expected = [
            "NA_STRINGS",
            "cache_url",
            "categorize",
            "drop_nested_columns",
            "fill_lines",
            "join_url",
            "list_remote_dir",
            "read",
            "sanitize_na",
            "sanitize_percent",
            "transmit",
            "uncategorize",
            "write",
        ]
        for name in expected:
            assert hasattr(pipette, name), f"Missing: {name}"

    def test_removed_names(self) -> None:
        import pipette

        removed = [
            "PIPETTE_TESTS_URL",
            "assign_and_save_data",
            "atomize",
            "decode",
            "droplevels",
            "encode",
            "export_data",
            "factorize",
            "get_json",
            "get_url_dir_list",
            "import_data",
            "init_dir",
            "load_data",
            "load_data_as_name",
            "load_remote_data",
            "match_rowname_column",
            "md5",
            "metadata2",
            "na_strings",
            "paste_url",
            "remove_na",
            "save_data",
            "sha256",
            "unfactorize",
        ]
        for name in removed:
            assert not hasattr(pipette, name), f"Should be removed: {name}"
