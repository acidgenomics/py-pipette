"""Import data from various file formats."""

import contextlib
import json
import os
import pickle
import re
from typing import Any

import pandas as pd

from pipette._file_utils import (
    _FORMAT_MAP,
    base_ext,
    compress_ext,
    decompress_file,
    local_or_remote_file,
)
from pipette._globals import NA_STRINGS
from pipette._match_rowname_column import match_rowname_column

_R_ONLY_FORMATS = {"rds", "rda"}
_GENOMICS_FORMATS = {
    "bam",
    "sam",
    "cram",
    "vcf",
    "bcf",
    "gff",
    "gtf",
    "bed",
    "bigwig",
    "bigbed",
    "wig",
    "fasta",
    "fastq",
    "obo",
    "maf",
    "pzfx",
}


def import_data(
    path: str,
    format: str | None = None,
    rownames: bool = True,
    colnames: bool | list[str] = True,
    skip: int = 0,
    nmax: int | None = None,
    comment: str | None = None,
    na_strings: list[str] | None = None,
    make_names: bool = True,
    quiet: bool = False,
    sheet: int | str | None = None,
    **kwargs: Any,
) -> Any:
    """Import data from a file.

    Parameters
    ----------
    path : str
        Local file path or URL.
    format : str, optional
        Force a specific format (e.g. ``"csv"``). Auto-detected by default.
    rownames : bool
        Detect and set row names from column.
    colnames : bool or list of str
        Use first row as column names, or provide custom names.
    skip : int
        Number of rows to skip.
    nmax : int, optional
        Maximum number of rows to read.
    comment : str, optional
        Lines starting with this are filtered (for lines format).
    na_strings : list of str, optional
        Strings to treat as NA.
    make_names : bool
        Sanitize column names to valid Python identifiers.
    quiet : bool
        Suppress messages.
    sheet : int or str, optional
        Sheet name or index for Excel files.
    **kwargs
        Extra arguments passed to the underlying reader.

    Returns
    -------
    pd.DataFrame, dict, list, or other
        Imported data, type depends on format.
    """
    if na_strings is None:
        na_strings = NA_STRINGS
    with local_or_remote_file(path) as local_path:
        if not quiet:
            print(f"Importing {path}")
        fmt = format
        if fmt is None:
            ext = base_ext(local_path)
            fmt = _FORMAT_MAP.get(ext)
            if fmt is None:
                raise ValueError(
                    f"Cannot detect format for {path!r} "
                    f"(extension: {ext!r}). "
                    f"Use the 'format' argument to specify."
                )
        if fmt in _R_ONLY_FORMATS:
            raise ValueError(
                f"R-specific format {fmt!r} is not supported in Python. "
                f"Use rpy2 or convert to CSV/Parquet first."
            )
        if fmt in _GENOMICS_FORMATS:
            raise ValueError(
                f"Genomics format {fmt!r} is not directly supported. "
                f"Use pysam, pyranges, or pybedtools instead."
            )
        comp = compress_ext(local_path)
        if comp is not None and fmt not in ("mtx",):
            decompressed = decompress_file(local_path)
            try:
                return _import_by_format(
                    decompressed,
                    fmt,
                    rownames=rownames,
                    colnames=colnames,
                    skip=skip,
                    nmax=nmax,
                    comment=comment,
                    na_strings=na_strings,
                    make_names=make_names,
                    sheet=sheet,
                    **kwargs,
                )
            finally:
                if decompressed != local_path and os.path.exists(decompressed):
                    os.unlink(decompressed)
        return _import_by_format(
            local_path,
            fmt,
            rownames=rownames,
            colnames=colnames,
            skip=skip,
            nmax=nmax,
            comment=comment,
            na_strings=na_strings,
            make_names=make_names,
            sheet=sheet,
            **kwargs,
        )


def _import_by_format(path: str, fmt: str, **kwargs: Any) -> Any:
    """Dispatch import to format-specific handler."""
    handlers = {
        "csv": _import_delim,
        "tsv": _import_delim,
        "json": _import_json,
        "yaml": _import_yaml,
        "excel": _import_excel,
        "pickle": _import_pickle,
        "lines": _import_lines,
        "gmt": _import_gmt,
        "gmx": _import_gmx,
        "grp": _import_grp,
        "gct": _import_gct,
        "gaf": _import_gaf,
        "mtx": _import_mtx,
        "parquet": _import_parquet,
        "feather": _import_feather,
        "hdf5": _import_hdf5,
    }
    handler = handlers.get(fmt)
    if handler is None:
        raise ValueError(f"No handler for format: {fmt!r}")
    if fmt == "csv":
        kwargs["sep"] = ","
    elif fmt == "tsv":
        kwargs["sep"] = "\t"
    return handler(path, **kwargs)


def _import_delim(
    path: str,
    sep: str = ",",
    rownames: bool = True,
    colnames: bool | list[str] = True,
    skip: int = 0,
    nmax: int | None = None,
    comment: str | None = None,
    na_strings: list[str] | None = None,
    make_names: bool = True,
    **kwargs: Any,
) -> pd.DataFrame:
    """Import delimited file (CSV/TSV)."""
    header = 0 if colnames is True else None
    names = colnames if isinstance(colnames, list) else None
    nrows = nmax
    df = pd.read_csv(
        path,
        sep=sep,
        header=header,
        names=names,
        skiprows=skip if skip else None,
        nrows=nrows,
        na_values=na_strings,
        keep_default_na=False,
        comment=comment,
        dtype=str,
        **{k: v for k, v in kwargs.items() if k not in ("sheet",)},
    )
    if make_names and colnames is not False:
        df.columns = _make_valid_names(list(df.columns))
    return _return_import(df, rownames=rownames)


def _import_json(path: str, **kwargs: Any) -> Any:
    """Import JSON file."""
    with open(path) as f:
        return json.load(f)


def _import_yaml(path: str, **kwargs: Any) -> Any:
    """Import YAML file."""
    try:
        import yaml  # noqa: PLC0415
    except ImportError as err:
        raise ImportError(
            "pyyaml is required for YAML support. Install it with: pip install pyyaml"
        ) from err
    with open(path) as f:
        return yaml.safe_load(f)


def _import_excel(
    path: str,
    sheet: int | str | None = None,
    rownames: bool = True,
    colnames: bool | list[str] = True,
    make_names: bool = True,
    na_strings: list[str] | None = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """Import Excel file."""
    try:
        import openpyxl  # noqa: F401, PLC0415
    except ImportError as err:
        raise ImportError(
            "openpyxl is required for Excel support. Install it with: pip install openpyxl"
        ) from err
    header = 0 if colnames is True else None
    names = colnames if isinstance(colnames, list) else None
    df = pd.read_excel(
        path,
        sheet_name=sheet or 0,
        header=header,
        names=names,
        na_values=na_strings,
        keep_default_na=False,
        dtype=str,
    )
    if make_names and colnames is not False:
        df.columns = _make_valid_names(list(df.columns))
    return _return_import(df, rownames=rownames)


def _import_pickle(path: str, **kwargs: Any) -> Any:
    """Import pickle file."""
    with open(path, "rb") as f:
        return pickle.load(f)


def _import_lines(path: str, comment: str | None = None, **kwargs: Any) -> list[str]:
    """Import file as list of lines."""
    with open(path) as f:
        lines = [line.rstrip("\n\r") for line in f]
    if comment:
        lines = [line for line in lines if not line.startswith(comment)]
    lines = [line for line in lines if line]
    return lines


def _import_gmt(path: str, **kwargs: Any) -> dict[str, list[str]]:
    """Import GMT (Gene Matrix Transposed) file."""
    result: dict[str, list[str]] = {}
    with open(path) as f:
        for line in f:
            parts = line.rstrip("\n\r").split("\t")
            if len(parts) < 3:
                continue
            name = parts[0]
            genes = [g for g in parts[2:] if g]
            result[name] = genes
    return result


def _import_gmx(path: str, **kwargs: Any) -> dict[str, list[str]]:
    """Import GMX file."""
    with open(path) as f:
        lines = [line.rstrip("\n\r").split("\t") for line in f]
    if not lines:
        return {}
    names = lines[0]
    result: dict[str, list[str]] = {}
    for i, name in enumerate(names):
        genes = []
        for row in lines[2:]:
            if i < len(row) and row[i]:
                genes.append(row[i])
        result[name] = genes
    return result


def _import_grp(path: str, **kwargs: Any) -> list[str]:
    """Import GRP file."""
    with open(path) as f:
        return [line.rstrip("\n\r") for line in f if line.strip() and not line.startswith("#")]


def _import_gct(
    path: str, rownames: bool = True, make_names: bool = True, **kwargs: Any
) -> pd.DataFrame:
    """Import GCT file."""
    with open(path) as f:
        f.readline().rstrip()
        f.readline().rstrip().split("\t")
    skip = 2
    df = pd.read_csv(path, sep="\t", skiprows=skip, dtype=str)
    if "Description" in df.columns:
        df = df.drop(columns=["Description"])
    if "NAME" in df.columns:
        df = df.rename(columns={"NAME": "rowname"})
    if make_names:
        df.columns = _make_valid_names(list(df.columns))
    return _return_import(df, rownames=rownames)


def _import_gaf(
    path: str, rownames: bool = True, make_names: bool = True, **kwargs: Any
) -> pd.DataFrame:
    """Import GAF (Gene Association Format) file."""
    cols = [
        "db",
        "db_object_id",
        "db_object_symbol",
        "qualifier",
        "go_id",
        "db_reference",
        "evidence_code",
        "with_from",
        "aspect",
        "db_object_name",
        "db_object_synonym",
        "db_object_type",
        "taxon",
        "date",
        "assigned_by",
        "annotation_extension",
        "gene_product_form_id",
    ]
    df = pd.read_csv(
        path,
        sep="\t",
        comment="!",
        header=None,
        names=cols,
        dtype=str,
    )
    return df


def _import_mtx(path: str, rownames: bool = True, **kwargs: Any) -> Any:
    """Import MTX (Matrix Market) file."""
    try:
        from scipy.io import mmread  # noqa: PLC0415
    except ImportError as err:
        raise ImportError(
            "scipy is required for MTX support. Install it with: pip install scipy"
        ) from err
    mat = mmread(path)
    return mat


def _import_parquet(
    path: str, rownames: bool = True, make_names: bool = True, **kwargs: Any
) -> pd.DataFrame:
    """Import Parquet file."""
    try:
        import pyarrow.parquet as pq  # noqa: PLC0415
    except ImportError as err:
        raise ImportError(
            "pyarrow is required for Parquet support. Install it with: pip install pyarrow"
        ) from err
    df = pq.read_table(path).to_pandas()
    if make_names:
        df.columns = _make_valid_names(list(df.columns))
    return _return_import(df, rownames=rownames)


def _import_feather(
    path: str, rownames: bool = True, make_names: bool = True, **kwargs: Any
) -> pd.DataFrame:
    """Import Feather/Arrow IPC file."""
    try:
        import pyarrow.feather as pf  # noqa: PLC0415
    except ImportError as err:
        raise ImportError(
            "pyarrow is required for Feather support. Install it with: pip install pyarrow"
        ) from err
    df = pf.read_feather(path)
    if make_names:
        df.columns = _make_valid_names(list(df.columns))
    return _return_import(df, rownames=rownames)


def _import_hdf5(path: str, rownames: bool = True, make_names: bool = True, **kwargs: Any) -> Any:
    """Import HDF5 file."""
    df = pd.read_hdf(path)
    if isinstance(df, pd.DataFrame):
        if make_names:
            df.columns = _make_valid_names(list(df.columns))
        return _return_import(df, rownames=rownames)
    return df


def _return_import(df: pd.DataFrame, rownames: bool = True) -> pd.DataFrame:
    """Post-process imported DataFrame.

    Detects row name column and sets it as the index.
    Coerces numeric columns from string.
    """
    if not isinstance(df, pd.DataFrame):
        return df
    for col in df.columns:
        if df[col].dtype == object:
            with contextlib.suppress(ValueError, TypeError):
                df[col] = pd.to_numeric(df[col])
    if rownames:
        rn_col = match_rowname_column(df)
        if rn_col is not None:
            df = df.set_index(rn_col)
            df.index.name = None
    return df


def _make_valid_names(names: list[str]) -> list[str]:
    """Make syntactically valid Python-style column names."""
    result = []
    for name in names:
        s = str(name)
        s = re.sub(r"[^a-zA-Z0-9_]", "_", s)
        s = re.sub(r"_+", "_", s)
        s = s.strip("_")
        if not s:
            s = "x"
        if s[0].isdigit():
            s = "x" + s
        result.append(s)
    return result
