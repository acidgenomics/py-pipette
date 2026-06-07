"""Save and load data utilities matching R's assignAndSaveData / loadDataAsName."""

import os
from typing import Any

from pipette._export import export_data
from pipette._import import import_data


def assign_and_save_data(
    name: str,
    obj: Any,
    *,
    dir: str = ".",
    ext: str = "pickle",
    overwrite: bool = True,
    quiet: bool = False,
) -> str:
    """Save an object to a file named after ``name``.

    Equivalent to R's ``assignAndSaveData``: saves ``obj`` to
    ``{dir}/{name}.{ext}`` via :func:`export_data`. Returns the file path.

    Parameters
    ----------
    name : str
        File base name (no extension).
    obj : object
        Object to save.
    dir : str
        Output directory. Created if it does not exist.
    ext : str
        File extension determining the format (e.g. ``"pickle"``,
        ``"csv"``, ``"parquet"``). Default ``"pickle"`` (replaces R's
        default ``.rds``).
    overwrite : bool
        Overwrite existing file.
    quiet : bool
        Suppress messages.

    Returns
    -------
    str
        Path to the saved file.

    Examples
    --------
    >>> import tempfile, os
    >>> with tempfile.TemporaryDirectory() as d:
    ...     p = assign_and_save_data("myobj", {"x": 1}, dir=d)
    ...     os.path.basename(p)
    'myobj.pickle'
    """
    path = os.path.join(dir, f"{name}.{ext}")
    return export_data(obj, path, overwrite=overwrite, quiet=quiet)


def load_data_as_name(
    *mappings: tuple[str, str],
    dir: str = ".",
    quiet: bool = False,
) -> dict[str, Any]:
    """Load files with custom name mapping.

    Equivalent to R's ``loadDataAsName``: loads each file and returns a
    dict mapping the requested names to the loaded objects. R's NSE
    ``newName = oldFile`` syntax becomes explicit tuples
    ``(new_name, old_file)``.

    Parameters
    ----------
    *mappings : tuple[str, str]
        Each mapping is ``(new_name, old_file)`` where ``old_file`` is
        the filename (without extension) or a full path relative to
        ``dir``.
    dir : str
        Base directory to look up relative file names.
    quiet : bool
        Suppress messages.

    Returns
    -------
    dict[str, Any]
        Mapping of ``{new_name: loaded_object}``.

    Examples
    --------
    >>> import tempfile, os
    >>> with tempfile.TemporaryDirectory() as d:
    ...     assign_and_save_data("src", [1, 2, 3], dir=d)
    ...     result = load_data_as_name(("dest", "src"), dir=d)
    ...     result["dest"]
    '/...src.pickle'
    [1, 2, 3]
    """
    result: dict[str, Any] = {}
    for new_name, old_file in mappings:
        # If old_file is already an absolute/relative path, use it directly.
        if os.path.isabs(old_file) or os.path.isfile(old_file):
            path = old_file
        else:
            # Search dir for a file matching old_file (with any extension).
            found = None
            if os.path.isdir(dir):
                for fname in os.listdir(dir):
                    base = os.path.splitext(fname)[0]
                    if base == old_file:
                        found = os.path.join(dir, fname)
                        break
            if found is None:
                msg = f"File {old_file!r} not found in {dir!r}."
                raise FileNotFoundError(msg)
            path = found
        result[new_name] = import_data(path, quiet=quiet)
    return result
