# pipette

[![Install with Bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg)](https://bioconda.github.io/recipes/pipette/README.html) ![Lifecycle: experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)

Unified reading and writing of data in Python.

## Installation

### [uv][] method

This is a [Python][] package hosted on [PyPI][] as `acidgenomics-pipette`.
The import name is unchanged: `pipette`.
We recommend using [uv][] to install.

```sh
uv add 'acidgenomics-pipette[extra]'
```

Or with [pip][]:

```sh
pip install 'acidgenomics-pipette[extra]'
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

### Read

```python
import pipette

# Read a CSV file.
df = pipette.read("data.csv")

# Read a TSV file.
df = pipette.read("data.tsv")

# Read an Excel file (requires openpyxl).
df = pipette.read("data.xlsx")

# Read JSON.
data = pipette.read("data.json")

# Read from a URL.
df = pipette.read("https://example.com/data.csv")
```

### Write

```python
import pandas as pd
import pipette

df = pd.DataFrame(
    {"sample1": [1, 2, 3], "sample2": [4, 5, 6]},
    index=["gene1", "gene2", "gene3"],
)

# Write to CSV.
pipette.write(df, "output.csv")

# Write to TSV.
pipette.write(df, "output.tsv")

# Write compressed.
pipette.write(df, "output.csv.gz")
```

### Data Transformation

```python
# Sanitize NA values in string columns.
df = pipette.sanitize_na(df)

# Convert columns with duplicates to categorical.
df = pipette.categorize(df)

# Convert categorical columns back to their underlying type.
df = pipette.uncategorize(df)

# Drop columns holding nested (non-scalar) values.
df = pipette.drop_nested_columns(df)
```

## Supported Formats

### Read

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

### Write

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
[pip]: https://pip.pypa.io/
[pypi]: https://pypi.org/project/acidgenomics-pipette/
[python]: https://www.python.org/
[uv]: https://docs.astral.sh/uv/

## License

Apache-2.0 — Copyright 2026 Acid Genomics LLC — see [LICENSE](LICENSE).
