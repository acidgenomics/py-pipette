# pipette

[![Install with Bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg)](https://bioconda.github.io/recipes/pipette/README.html) ![Lifecycle: maturing](https://img.shields.io/badge/lifecycle-maturing-blue.svg)

Unified import and export of data in Python.

## Installation

### [uv][] method

This is a [Python][] package hosted at [python.acidgenomics.com][].
We recommend using [uv][] to install.

```sh
uv pip install \
    --index-url 'https://python.acidgenomics.com/simple/' \
    'pipette[extra]'
```

Or add the index to your project's `pyproject.toml`:

```toml
[[tool.uv.index]]
url = "https://python.acidgenomics.com/simple/"
```

Then install:

```sh
uv add 'pipette[extra]'
```

### [Conda][] method

Configure [Conda][] to use the [Bioconda][] channels.

```sh
# Don't install recipe into base environment.
name='pipette'
conda create --name="$name" "$name"
conda activate "$name"
python -c 'import pipette'
```

Conda has no equivalent of Python extras. For the optional format support that
`pipette[extra]` provides, add the dependencies to the environment:
`conda create --name="$name" "$name" openpyxl pyarrow pyyaml scipy`.

## Quick Start

### Import

```python
import pipette

# Import a CSV file.
df = pipette.import_data("data.csv")

# Import a TSV file.
df = pipette.import_data("data.tsv")

# Import an Excel file (requires openpyxl).
df = pipette.import_data("data.xlsx")

# Import JSON.
data = pipette.import_data("data.json")

# Import from a URL.
df = pipette.import_data("https://example.com/data.csv")
```

### Export

```python
import pandas as pd
import pipette

df = pd.DataFrame(
    {"sample1": [1, 2, 3], "sample2": [4, 5, 6]},
    index=["gene1", "gene2", "gene3"],
)

# Export to CSV.
pipette.export_data(df, "output.csv")

# Export to TSV.
pipette.export_data(df, "output.tsv")

# Export compressed.
pipette.export_data(df, "output.csv.gz")
```

### Data Transformation

```python
# Sanitize NA values in string columns.
df = pipette.sanitize_na(df)

# Remove all-NA rows and columns.
df = pipette.remove_na(df)

# Convert columns with duplicates to categorical.
df = pipette.factorize(df)

# Convert categorical columns back to atomic types.
df = pipette.unfactorize(df)

# Keep only scalar columns.
df = pipette.atomize(df)
```

### Checksums

```python
# Get MD5 checksum of a file.
checksum = pipette.md5("file.csv")

# Get SHA-256 checksum of a file.
checksum = pipette.sha256("file.csv")
```

## Supported Formats

### Import

| Format         | Extension                   | Dependencies |
|:---------------|:----------------------------|:-------------|
| CSV            | `.csv`                      | -            |
| TSV            | `.tsv`, `.tab`              | -            |
| Excel          | `.xlsx`, `.xls`             | openpyxl     |
| JSON           | `.json`                     | -            |
| YAML           | `.yml`, `.yaml`             | pyyaml       |
| Pickle         | `.pickle`, `.pkl`           | -            |
| Lines          | `.txt`, `.log`, `.list`     | -            |
| GMT            | `.gmt`                      | -            |
| GMX            | `.gmx`                      | -            |
| GRP            | `.grp`                      | -            |
| GCT            | `.gct`                      | -            |
| GAF            | `.gaf`                      | -            |
| MTX            | `.mtx`, `.mtx.gz`           | scipy        |
| Parquet        | `.parquet`                  | pyarrow      |
| Feather/Arrow  | `.feather`, `.arrow`        | pyarrow      |
| HDF5           | `.h5`, `.hdf5`              | -            |

### Export

| Format         | Extension                   | Dependencies |
|:---------------|:----------------------------|:-------------|
| CSV            | `.csv`                      | -            |
| TSV            | `.tsv`, `.tab`              | -            |
| JSON           | `.json`                     | -            |
| YAML           | `.yml`, `.yaml`             | pyyaml       |
| Pickle         | `.pickle`, `.pkl`           | -            |
| Lines          | `.txt`, `.log`              | -            |

Compressed output is supported via `.gz`, `.bz2`, `.xz`, and `.zip` suffixes.

## Optional Dependencies

- **openpyxl**: Excel file support.
- **pyarrow**: Parquet and Feather file support.
- **pyyaml**: YAML file support.
- **scipy**: MTX (Matrix Market) sparse matrix support.

[bioconda]: https://bioconda.github.io/
[conda]: https://docs.conda.io/
[python]: https://www.python.org/
[python.acidgenomics.com]: https://python.acidgenomics.com
[uv]: https://docs.astral.sh/uv/


## License

Apache-2.0 — Copyright 2026 Acid Genomics LLC — see [LICENSE](LICENSE).
