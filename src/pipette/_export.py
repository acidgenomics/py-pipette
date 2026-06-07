"""Export data to various file formats."""

import json
import os
import pickle
import tempfile
from typing import Any

import pandas as pd

from pipette._file_utils import (
    _FORMAT_MAP,
    base_ext,
    compress_ext,
    compress_file,
    init_dir,
)
from pipette._s3 import _is_s3_uri, _s3_upload


def export_data(
    x: Any,
    path: str,
    *,
    overwrite: bool = True,
    rownames: bool = True,
    quiet: bool = False,
    **kwargs: Any,
) -> str:
    """Export data to a file.

    Parameters
    ----------
    x : object
        Data to export. DataFrames, dicts, lists, and other types
        are supported depending on the format.
    path : str
        Output file path. Supports local paths and ``s3://`` URIs.
    overwrite : bool
        Overwrite existing files. Raises ``FileExistsError`` if False
        and the file exists.
    rownames : bool
        Include row names (index) in the output.
    quiet : bool
        Suppress messages.
    **kwargs
        Extra arguments passed to the underlying writer.

    Returns
    -------
    str
        Path to the exported file.
    """
    if _is_s3_uri(path):
        ext = base_ext(path)
        with tempfile.NamedTemporaryFile(suffix="." + ext if ext else "", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            _do_export(x, tmp_path, rownames=rownames, quiet=quiet, **kwargs)
            _s3_upload(tmp_path, path, quiet=quiet)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        return path
    if not overwrite and os.path.isfile(path):
        raise FileExistsError(f"File exists: {path!r}. Use overwrite=True to replace.")
    parent = os.path.dirname(path)
    if parent:
        init_dir(parent)
    return _do_export(x, path, rownames=rownames, quiet=quiet, **kwargs)


def _do_export(
    x: Any,
    path: str,
    *,
    rownames: bool = True,
    quiet: bool = False,
    **kwargs: Any,
) -> str:
    """Write data to a local path."""
    comp = compress_ext(path)
    ext = base_ext(path)
    fmt = _FORMAT_MAP.get(ext)
    if fmt is None:
        msg = f"Cannot detect format for {path!r} (extension: {ext!r})."
        raise ValueError(msg)
    if not quiet:
        print(f"Exporting {path}")
    if comp is not None:
        stem = path
        for c in (".gz", ".bz2", ".xz", ".zip"):
            if stem.endswith(c):
                stem = stem[: -len(c)]
                break
        _export_by_format(x, stem, fmt, rownames=rownames, **kwargs)
        compress_file(stem, ext=comp)
        os.unlink(stem)
    else:
        _export_by_format(x, path, fmt, rownames=rownames, **kwargs)
    return path


def _export_by_format(x: Any, path: str, fmt: str, rownames: bool = True, **kwargs: Any) -> None:
    """Dispatch export to format-specific handler."""
    if fmt in ("csv", "tsv"):
        sep = "," if fmt == "csv" else "\t"
        _export_dataframe(x, path, sep=sep, rownames=rownames, **kwargs)
    elif fmt == "json":
        _export_json(x, path, **kwargs)
    elif fmt == "yaml":
        _export_yaml(x, path, **kwargs)
    elif fmt == "pickle":
        _export_pickle(x, path, **kwargs)
    elif fmt == "lines":
        _export_lines(x, path, **kwargs)
    elif fmt == "parquet":
        _export_parquet(x, path, rownames=rownames, **kwargs)
    elif fmt == "feather":
        _export_feather(x, path, **kwargs)
    elif fmt == "excel":
        _export_excel(x, path, rownames=rownames, **kwargs)
    elif fmt == "hdf5":
        _export_hdf5(x, path, **kwargs)
    else:
        msg = f"Export not supported for format: {fmt!r}"
        raise ValueError(msg)


def _export_dataframe(
    x: Any, path: str, sep: str = ",", rownames: bool = True, **kwargs: Any
) -> None:
    """Export DataFrame to delimited file."""
    if not isinstance(x, pd.DataFrame):
        x = pd.DataFrame(x)
    if (rownames and x.index.name is not None) or (
        rownames and not isinstance(x.index, pd.RangeIndex)
    ):
        df = x.copy()
        df.insert(0, "rowname", df.index)
        df = df.reset_index(drop=True)
        df.to_csv(path, sep=sep, index=False)
    else:
        x.to_csv(path, sep=sep, index=False)


def _export_json(x: Any, path: str, **kwargs: Any) -> None:
    """Export to JSON file."""
    with open(path, "w") as f:
        json.dump(x, f, indent=2, default=str)


def _export_yaml(x: Any, path: str, **kwargs: Any) -> None:
    """Export to YAML file."""
    try:
        import yaml  # noqa: PLC0415
    except ImportError as err:
        msg = "pyyaml is required for YAML export. Install it with: pip install pyyaml"
        raise ImportError(msg) from err
    with open(path, "w") as f:
        yaml.dump(x, f, default_flow_style=False)


def _export_pickle(x: Any, path: str, **kwargs: Any) -> None:
    """Export to pickle file."""
    with open(path, "wb") as f:
        pickle.dump(x, f)


def _export_lines(x: Any, path: str, **kwargs: Any) -> None:
    """Export list to text file (one item per line)."""
    if isinstance(x, (list, tuple)):
        lines = x
    elif isinstance(x, pd.Series):
        lines = x.tolist()
    else:
        lines = [str(x)]
    with open(path, "w") as f:
        for line in lines:
            f.write(str(line) + "\n")


def _export_parquet(x: Any, path: str, rownames: bool = True, **kwargs: Any) -> None:
    """Export DataFrame to Parquet file."""
    try:
        import pyarrow  # noqa: F401, PLC0415
    except ImportError as err:
        msg = "pyarrow is required for Parquet export. Install it with: pip install pyarrow"
        raise ImportError(msg) from err
    if not isinstance(x, pd.DataFrame):
        x = pd.DataFrame(x)
    index = rownames and x.index.name is not None
    x.to_parquet(path, index=index, **kwargs)


def _export_feather(x: Any, path: str, **kwargs: Any) -> None:
    """Export DataFrame to Feather file."""
    try:
        import pyarrow  # noqa: F401, PLC0415
    except ImportError as err:
        msg = "pyarrow is required for Feather export. Install it with: pip install pyarrow"
        raise ImportError(msg) from err
    if not isinstance(x, pd.DataFrame):
        x = pd.DataFrame(x)
    x.to_feather(path, **kwargs)


def _export_excel(x: Any, path: str, rownames: bool = True, **kwargs: Any) -> None:
    """Export DataFrame to Excel file."""
    try:
        import openpyxl  # noqa: F401, PLC0415
    except ImportError as err:
        msg = "openpyxl is required for Excel export. Install it with: pip install openpyxl"
        raise ImportError(msg) from err
    if not isinstance(x, pd.DataFrame):
        x = pd.DataFrame(x)
    index = rownames and x.index.name is not None
    x.to_excel(path, index=index, engine="openpyxl", **kwargs)


def _export_hdf5(x: Any, path: str, *, key: str = "data", **kwargs: Any) -> None:
    """Export DataFrame to HDF5 file."""
    try:
        import tables  # noqa: F401, PLC0415
    except ImportError as err:
        msg = "tables is required for HDF5 export. Install it with: pip install tables"
        raise ImportError(msg) from err
    if not isinstance(x, pd.DataFrame):
        x = pd.DataFrame(x)
    x.to_hdf(path, key=key, **kwargs)
