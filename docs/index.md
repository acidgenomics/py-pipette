# pipette

Unified import and export of data in Python.

The package provides a single `import_data`/`export_data` entry point that dispatches
on file extension across a wide range of bioinformatics and general-purpose formats,
plus data-sanitization helpers (NA handling, categorical conversion) and file
checksums.

## Installation

### uv method

This package is hosted at [python.acidgenomics.com](https://python.acidgenomics.com/).
We recommend using [uv](https://docs.astral.sh/uv/) to install.

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

## Import

```pycon
>>> import pipette
>>> df = pipette.import_data("data.csv")  # doctest: +SKIP
>>> df = pipette.import_data("data.tsv")  # doctest: +SKIP
>>> df = pipette.import_data("data.xlsx")  # doctest: +SKIP  (requires openpyxl)
>>> data = pipette.import_data("data.json")  # doctest: +SKIP
>>> df = pipette.import_data("https://example.com/data.csv")  # doctest: +SKIP
```

`import_data` dispatches on file extension, and understands a URL or a local path
equally:

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

## Export

```pycon
>>> import pandas as pd
>>> df = pd.DataFrame(
...     {"sample1": [1, 2, 3], "sample2": [4, 5, 6]},
...     index=["gene1", "gene2", "gene3"],
... )
>>> pipette.export_data(df, "output.csv")  # doctest: +SKIP
>>> pipette.export_data(df, "output.tsv")  # doctest: +SKIP
>>> pipette.export_data(df, "output.csv.gz")  # doctest: +SKIP
```

`export_data` supports CSV, TSV, JSON, YAML, pickle, and lines formats, with
compressed output via `.gz`, `.bz2`, `.xz`, or `.zip` suffixes.

## Data sanitization

```pycon
>>> df = pipette.sanitize_na(df)  # doctest: +SKIP
>>> df = pipette.remove_na(df)  # doctest: +SKIP
>>> df = pipette.factorize(df)  # doctest: +SKIP
>>> df = pipette.unfactorize(df)  # doctest: +SKIP
>>> df = pipette.atomize(df)  # doctest: +SKIP
```

`sanitize_na` replaces NA-like strings (`na_strings`, aliased as `NA_STRINGS`) with
`NaN`; `remove_na` drops all-NA rows/columns; `factorize`/`unfactorize` convert
duplicated string columns to/from `Categorical`; `atomize` keeps only scalar-valued
columns.

## Checksums

```pycon
>>> pipette.md5("file.csv")  # doctest: +SKIP
>>> pipette.sha256("file.csv")  # doctest: +SKIP
```

## Saved Python objects

`load_data`, `save_data`, `load_data_as_name`, `assign_and_save_data`, and
`load_remote_data` save and restore arbitrary Python objects as pickles, including
loading a saved object under a new variable name.

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
