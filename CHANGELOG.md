# Changelog

## 0.2.1 (2026-09-01)

### Changes

- Rename the PyPI distribution to `acidgenomics-pipette`. The import name is
  unchanged: `import pipette` still works.
- Publish to PyPI instead of `python.acidgenomics.com` only.

## 0.2.0 (2026-08-21)

### Breaking changes

- Rename `import_data()` to `read()`; rename `export_data()` to `write()`.
- Remove `load_data()`, `save_data()`, `assign_and_save_data()`, and
  `load_remote_data()`. Build the path with `pathlib.Path` and call `read`/
  `write` directly, or use `pipette.cache_url()` for a remote file.
- Remove `load_data_as_name()`. It has no Python equivalent: it exists in R
  because `load()` dumps saved object names into the calling environment, so R
  needs a hook to bind a different name. Python already binds whatever name
  you write, e.g. `new = pipette.read(path)`.
- Rename `encode()`/`decode()` and remove `factorize()`/`unfactorize()`,
  merging all four into `categorize()`/`uncategorize()`. Their `j=` parameter
  is now `columns=`.
- Rename `atomize()` to `drop_nested_columns()`.
- Rename `paste_url()` to `join_url()`. Its `protocol="none"` sentinel is now
  `protocol=None`.
- Rename `get_url_dir_list()` to `list_remote_dir()`.
- Remove `metadata2()`. Use `df.attrs` directly.
- Remove `droplevels()`. Use
  `df[col] = df[col].cat.remove_unused_categories()` directly.
- Remove `remove_na()`. Use `df.dropna()` directly.
- Remove `md5()` and `sha256()`. Use `hashlib.file_digest()` (stdlib since
  Python 3.11) directly.
- Remove `init_dir()`. Use `os.makedirs(path, exist_ok=True)` or
  `Path(path).mkdir(parents=True, exist_ok=True)` directly.
- Remove `get_json()`. Use `read(url, format="json")`.
- Remove `match_rowname_column()` from the public API; it is now private.
- Remove the `na_strings` alias; use `NA_STRINGS`.
- Remove the dead `PIPETTE_TESTS_URL` constant.
- `read()` and `write()` now take `str | os.PathLike`, so a `pathlib.Path`
  works everywhere a path is accepted.
- `read()`'s `rownames=` parameter is renamed to `index=`; same for `write()`.
- `write()` now returns the written path (a `Path` locally, or the `str` URI
  for an `s3://` target) instead of a bare `str`.
- `write()` gains a `format=` parameter, matching `read()`.
- Every parameter after the first positional argument on every public
  function is now keyword-only.

## 0.1.0 (2026-06-19)

### Changes

- Switch license to Apache-2.0.
- Publish to `python.acidgenomics.com` (private PEP 503 index).
- Update installation instructions in README.

---

## 0.0.1 (initial)

Initial release.
