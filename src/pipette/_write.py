"""Write data to various file formats."""

import json
import os
import pickle
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd

from pipette._file_utils import (
    _FORMAT_MAP,
    base_ext,
    compress_ext,
    compress_file,
)
from pipette._s3 import _is_s3_uri, _s3_upload


def write(
    obj: Any,
    path: str | os.PathLike[str],
    *,
    format: str | None = None,
    overwrite: bool = True,
    index: bool = True,
    quiet: bool = False,
    **kwargs: Any,
) -> Path | str:
    """Write data to a file.

    Parameters
    ----------
    obj : object
        Data to write. DataFrames, dicts, lists, and other types
        are supported depending on the format.
    path : str or os.PathLike
        Output file path. Supports local paths and ``s3://`` URIs.
    format : str, optional
        Force a specific format (e.g. ``"csv"``). Auto-detected from the
        extension by default.
    overwrite : bool
        Overwrite existing files. Raises ``FileExistsError`` if False
        and the file exists.
    index : bool
        Include the row index in the output.
    quiet : bool
        Suppress messages.
    **kwargs
        Extra arguments passed to the underlying writer.

    Returns
    -------
    pathlib.Path or str
        Path to the written file. A ``Path`` for a local target, or the
        ``str`` URI unchanged for an ``s3://`` target.
    """
    path = os.fspath(path)
    if _is_s3_uri(path):
        ext = base_ext(path)
        with tempfile.NamedTemporaryFile(suffix="." + ext if ext else "", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            _write_local(obj, tmp_path, format=format, index=index, quiet=quiet, **kwargs)
            _s3_upload(tmp_path, path, quiet=quiet)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        return path
    if not overwrite and os.path.isfile(path):
        raise FileExistsError(f"File exists: {path!r}. Use overwrite=True to replace.")
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    return Path(_write_local(obj, path, format=format, index=index, quiet=quiet, **kwargs))


def _write_local(
    obj: Any,
    path: str,
    *,
    format: str | None = None,
    index: bool = True,
    quiet: bool = False,
    **kwargs: Any,
) -> str:
    """Write data to a local path."""
    comp = compress_ext(path)
    ext = base_ext(path)
    fmt = format or _FORMAT_MAP.get(ext)
    if fmt is None:
        msg = f"Cannot detect format for {path!r} (extension: {ext!r})."
        raise ValueError(msg)
    if not quiet:
        print(f"Writing {path}")
    if comp is not None:
        stem = path
        for c in (".gz", ".bz2", ".xz", ".zip"):
            if stem.endswith(c):
                stem = stem[: -len(c)]
                break
        _write_by_format(obj, stem, fmt, index=index, **kwargs)
        compress_file(stem, ext=comp)
        os.unlink(stem)
    else:
        _write_by_format(obj, path, fmt, index=index, **kwargs)
    return path


def _write_by_format(obj: Any, path: str, fmt: str, *, index: bool = True, **kwargs: Any) -> None:
    """Dispatch write to a format-specific handler."""
    if fmt in ("csv", "tsv"):
        sep = "," if fmt == "csv" else "\t"
        _write_delim(obj, path, sep=sep, index=index, **kwargs)
    elif fmt == "json":
        _write_json(obj, path, **kwargs)
    elif fmt == "yaml":
        _write_yaml(obj, path, **kwargs)
    elif fmt == "pickle":
        _write_pickle(obj, path, **kwargs)
    elif fmt == "lines":
        _write_lines(obj, path, **kwargs)
    elif fmt == "parquet":
        _write_parquet(obj, path, index=index, **kwargs)
    elif fmt == "feather":
        _write_feather(obj, path, **kwargs)
    elif fmt == "excel":
        _write_excel(obj, path, index=index, **kwargs)
    elif fmt == "hdf5":
        _write_hdf5(obj, path, **kwargs)
    elif fmt == "gmt":
        _write_gmt(obj, path, **kwargs)
    elif fmt == "gmx":
        _write_gmx(obj, path, **kwargs)
    elif fmt == "grp":
        _write_grp(obj, path, **kwargs)
    elif fmt == "gct":
        _write_gct(obj, path, **kwargs)
    elif fmt == "gaf":
        _write_gaf(obj, path, **kwargs)
    elif fmt == "mtx":
        _write_mtx(obj, path, **kwargs)
    else:
        msg = f"Write not supported for format: {fmt!r}"
        raise ValueError(msg)


def _write_delim(obj: Any, path: str, *, sep: str = ",", index: bool = True, **kwargs: Any) -> None:
    """Write a DataFrame to a delimited file."""
    if not isinstance(obj, pd.DataFrame):
        obj = pd.DataFrame(obj)
    if (index and obj.index.name is not None) or (
        index and not isinstance(obj.index, pd.RangeIndex)
    ):
        df = obj.copy()
        df.insert(0, "rowname", df.index)
        df = df.reset_index(drop=True)
        df.to_csv(path, sep=sep, index=False)
    else:
        obj.to_csv(path, sep=sep, index=False)


def _write_json(obj: Any, path: str, **kwargs: Any) -> None:
    """Write to a JSON file."""
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=str)


def _write_yaml(obj: Any, path: str, **kwargs: Any) -> None:
    """Write to a YAML file."""
    try:
        import yaml  # noqa: PLC0415
    except ImportError as err:
        msg = "pyyaml is required for YAML export. Install it with: pip install pyyaml"
        raise ImportError(msg) from err
    with open(path, "w") as f:
        yaml.dump(obj, f, default_flow_style=False)


def _write_pickle(obj: Any, path: str, **kwargs: Any) -> None:
    """Write to a pickle file."""
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def _write_lines(obj: Any, path: str, **kwargs: Any) -> None:
    """Write a list to a text file (one item per line)."""
    if isinstance(obj, (list, tuple)):
        lines = obj
    elif isinstance(obj, pd.Series):
        lines = obj.tolist()
    else:
        lines = [str(obj)]
    with open(path, "w") as f:
        for line in lines:
            f.write(str(line) + "\n")


def _write_parquet(obj: Any, path: str, *, index: bool = True, **kwargs: Any) -> None:
    """Write a DataFrame to a Parquet file."""
    try:
        import pyarrow  # noqa: F401, PLC0415
    except ImportError as err:
        msg = "pyarrow is required for Parquet export. Install it with: pip install pyarrow"
        raise ImportError(msg) from err
    if not isinstance(obj, pd.DataFrame):
        obj = pd.DataFrame(obj)
    use_index = index and obj.index.name is not None
    obj.to_parquet(path, index=use_index, **kwargs)


def _write_feather(obj: Any, path: str, **kwargs: Any) -> None:
    """Write a DataFrame to a Feather file."""
    try:
        import pyarrow  # noqa: F401, PLC0415
    except ImportError as err:
        msg = "pyarrow is required for Feather export. Install it with: pip install pyarrow"
        raise ImportError(msg) from err
    if not isinstance(obj, pd.DataFrame):
        obj = pd.DataFrame(obj)
    obj.to_feather(path, **kwargs)


def _write_excel(obj: Any, path: str, *, index: bool = True, **kwargs: Any) -> None:
    """Write a DataFrame to an Excel file."""
    try:
        import openpyxl  # noqa: F401, PLC0415
    except ImportError as err:
        msg = "openpyxl is required for Excel export. Install it with: pip install openpyxl"
        raise ImportError(msg) from err
    if not isinstance(obj, pd.DataFrame):
        obj = pd.DataFrame(obj)
    use_index = index and obj.index.name is not None
    obj.to_excel(path, index=use_index, engine="openpyxl", **kwargs)


def _write_hdf5(obj: Any, path: str, *, key: str = "data", **kwargs: Any) -> None:
    """Write a DataFrame to an HDF5 file."""
    try:
        import tables  # noqa: F401, PLC0415  # type: ignore[import-untyped]
    except ImportError as err:
        msg = "tables is required for HDF5 export. Install it with: pip install tables"
        raise ImportError(msg) from err
    if not isinstance(obj, pd.DataFrame):
        obj = pd.DataFrame(obj)
    obj.to_hdf(path, key=key, **kwargs)


def _write_gmt(obj: dict[str, list[str]], path: str, **kwargs: Any) -> None:
    """Write a gene set dict to a GMT (Gene Matrix Transposed) file.

    Each entry writes one tab-separated line: name, description (empty), genes.
    """
    if not isinstance(obj, dict):
        msg = "GMT export requires a dict mapping set names to gene lists."
        raise TypeError(msg)
    with open(path, "w") as f:
        for name, genes in obj.items():
            f.write("\t".join([name, "", *list(genes)]) + "\n")


def _write_gmx(obj: dict[str, list[str]], path: str, **kwargs: Any) -> None:
    """Write a gene set dict to a GMX (vertical gene set) file.

    Header row = set names; second row = descriptions (empty);
    remaining rows = genes (padded with empty strings).
    """
    if not isinstance(obj, dict):
        msg = "GMX export requires a dict mapping set names to gene lists."
        raise TypeError(msg)
    names = list(obj.keys())
    gene_lists = [list(obj[n]) for n in names]
    max_len = max((len(g) for g in gene_lists), default=0)
    with open(path, "w") as f:
        f.write("\t".join(names) + "\n")
        f.write("\t".join("" for _ in names) + "\n")
        for i in range(max_len):
            row = [gl[i] if i < len(gl) else "" for gl in gene_lists]
            f.write("\t".join(row) + "\n")


def _write_grp(obj: list[str], path: str, **kwargs: Any) -> None:
    """Write a gene list to a GRP file (one gene per line)."""
    if isinstance(obj, pd.Series):
        obj = obj.tolist()
    if not isinstance(obj, (list, tuple)):
        msg = "GRP export requires a list of strings."
        raise TypeError(msg)
    with open(path, "w") as f:
        for item in obj:
            f.write(str(item) + "\n")


def _write_gct(obj: pd.DataFrame, path: str, **kwargs: Any) -> None:
    """Write a DataFrame to GCT (Gene Cluster Text) format.

    Writes version line ``#1.2``, dimension line, and data with
    Name and Description columns.
    """
    if not isinstance(obj, pd.DataFrame):
        msg = "GCT export requires a pandas DataFrame."
        raise TypeError(msg)
    n_rows, n_cols = obj.shape
    with open(path, "w") as f:
        f.write("#1.2\n")
        f.write(f"{n_rows}\t{n_cols}\n")
        # Header: Name, Description, then sample columns.
        header = ["Name", "Description", *list(obj.columns)]
        f.write("\t".join(header) + "\n")
        for idx, row in obj.iterrows():
            f.write("\t".join([str(idx), "na", *[str(v) for v in row]]) + "\n")


def _write_gaf(obj: pd.DataFrame, path: str, **kwargs: Any) -> None:
    """Write a DataFrame to a GAF (Gene Association Format) file."""
    if not isinstance(obj, pd.DataFrame):
        msg = "GAF export requires a pandas DataFrame."
        raise TypeError(msg)
    obj.to_csv(path, sep="\t", index=False, header=False)


def _write_mtx(obj: Any, path: str, **kwargs: Any) -> None:
    """Write a sparse matrix to an MTX (Matrix Market) file."""
    try:
        from scipy.io import mmwrite  # noqa: PLC0415
    except ImportError as err:
        msg = "scipy is required for MTX export. Install it with: pip install scipy"
        raise ImportError(msg) from err
    mmwrite(path, obj)
