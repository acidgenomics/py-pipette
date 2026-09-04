# pipette

Unified reading and writing of data in Python.

The package provides a single `read`/`write` entry point that dispatches
on file extension across a wide range of bioinformatics and general-purpose formats,
plus data-sanitization helpers for NA handling and categorical conversion.

## Installation

### uv method

This package is hosted on [PyPI](https://pypi.org/project/acidgenomics-pipette/)
as `acidgenomics-pipette`. The import name is unchanged: `pipette`.
We recommend using [uv](https://docs.astral.sh/uv/) to install.

```sh
uv add 'acidgenomics-pipette[extra]'
```

Or with [pip](https://pip.pypa.io/):

```sh
pip install 'acidgenomics-pipette[extra]'
```

### Conda method

Configure [Conda](https://docs.conda.io/) to use the
[Bioconda](https://bioconda.github.io/) channels.

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

## Read

```pycon
>>> import pipette
>>> df = pipette.read("data.csv")  # doctest: +SKIP
>>> df = pipette.read("data.tsv")  # doctest: +SKIP
>>> df = pipette.read("data.xlsx")  # doctest: +SKIP  (requires openpyxl)
>>> data = pipette.read("data.json")  # doctest: +SKIP
>>> df = pipette.read("https://example.com/data.csv")  # doctest: +SKIP
```

`read` dispatches on file extension, and understands a URL, a local path, or a
`pathlib.Path` equally:

| Format | Extension | Dependencies |
| --- | --- | --- |
| CSV | `.csv` | - |
| TSV | `.tsv`, `.tab` | - |
| Excel | `.xlsx`, `.xls` | openpyxl |
| JSON | `.json` | - |
| YAML | `.yml`, `.yaml` | pyyaml |
| Pickle | `.pickle`, `.pkl` | - |
| Lines | `.txt`, `.log`, `.list` | - |
| GMT | `.gmt` | - |
| GMX | `.gmx` | - |
| GRP | `.grp` | - |
| GCT | `.gct` | - |
| GAF | `.gaf` | - |
| MTX | `.mtx`, `.mtx.gz` | scipy |
| Parquet | `.parquet` | pyarrow |
| Feather/Arrow | `.feather`, `.arrow` | pyarrow |
| HDF5 | `.h5`, `.hdf5` | - |

## Write

```pycon
>>> import pandas as pd
>>> df = pd.DataFrame(
...     {"sample1": [1, 2, 3], "sample2": [4, 5, 6]},
...     index=["gene1", "gene2", "gene3"],
... )
>>> pipette.write(df, "output.csv")  # doctest: +SKIP
>>> pipette.write(df, "output.tsv")  # doctest: +SKIP
>>> pipette.write(df, "output.csv.gz")  # doctest: +SKIP
```

`write` supports CSV, TSV, JSON, YAML, pickle, and lines formats, with
compressed output via `.gz`, `.bz2`, `.xz`, or `.zip` suffixes. It returns the
written path: a `pathlib.Path` for a local target, or the `str` URI unchanged
for an `s3://` target.

## Data sanitization

```pycon
>>> df = pipette.sanitize_na(df)  # doctest: +SKIP
>>> df = pipette.categorize(df)  # doctest: +SKIP
>>> df = pipette.uncategorize(df)  # doctest: +SKIP
>>> df = pipette.drop_nested_columns(df)  # doctest: +SKIP
```

`sanitize_na` replaces NA-like strings (`na_strings`, aliased as `NA_STRINGS`) with
`NaN`; `categorize`/`uncategorize` convert duplicated string columns to/from
`Categorical`; `drop_nested_columns` keeps only scalar-valued columns.

## Optional dependencies

- **openpyxl**: Excel file support.
- **pyarrow**: Parquet and Feather file support.
- **pyyaml**: YAML file support.
- **scipy**: MTX (Matrix Market) sparse matrix support.

```{toctree}
:maxdepth: 1
:caption: Contents
:hidden:

reference/index
changelog
```
