"""Export data to various file formats."""

import json
import os
import pickle
from typing import Any

import pandas as pd

from pipette._file_utils import (
    _FORMAT_MAP,
    base_ext,
    compress_ext,
    compress_file,
    init_dir,
)


def export_data(
    x: Any,
    path: str,
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
        Output file path.
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
    if not overwrite and os.path.isfile(path):
        raise FileExistsError(f"File exists: {path!r}. Use overwrite=True to replace.")
    parent = os.path.dirname(path)
    if parent:
        init_dir(parent)
    comp = compress_ext(path)
    ext = base_ext(path)
    fmt = _FORMAT_MAP.get(ext)
    if fmt is None:
        raise ValueError(f"Cannot detect format for {path!r} (extension: {ext!r}).")
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


def _export_by_format(x: Any, path: str, fmt: str, **kwargs: Any) -> None:
    """Dispatch export to format-specific handler."""
    if fmt in ("csv", "tsv"):
        sep = "," if fmt == "csv" else "\t"
        _export_dataframe(x, path, sep=sep, **kwargs)
    elif fmt == "json":
        _export_json(x, path, **kwargs)
    elif fmt == "yaml":
        _export_yaml(x, path, **kwargs)
    elif fmt == "pickle":
        _export_pickle(x, path, **kwargs)
    elif fmt in ("lines",):
        _export_lines(x, path, **kwargs)
    else:
        raise ValueError(f"Export not supported for format: {fmt!r}")


def _export_dataframe(
    x: Any, path: str, sep: str = ",", rownames: bool = True, **kwargs: Any
) -> None:
    """Export DataFrame to delimited file."""
    if not isinstance(x, pd.DataFrame):
        x = pd.DataFrame(x)
    if (
        rownames
        and x.index.name is not None
        or (rownames and not isinstance(x.index, pd.RangeIndex))
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
        raise ImportError(
            "pyyaml is required for YAML export. Install it with: pip install pyyaml"
        ) from err
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
