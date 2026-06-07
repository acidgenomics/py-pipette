"""Global constants for pipette."""

NA_STRINGS: list[str] = [
    "",
    ".",
    "#N/A",
    "#n/a",
    "N/A",
    "NA",
    "NaN",
    "NULL",
    "None",
    "\\N",
    "_",
    "n/a",
    "na",
    "none",
    "null",
]
"""Strings treated as NA during import."""

PIPETTE_TESTS_URL: str = "https://r.acidgenomics.com/testdata/pipette"
"""Base URL for pipette test data files."""
