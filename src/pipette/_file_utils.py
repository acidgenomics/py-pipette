"""File utility functions for pipette."""

import bz2
import gzip
import lzma
import os
import re
import shutil
import tempfile
import urllib.request
import zipfile
from collections.abc import Generator
from contextlib import contextmanager

_COMPRESS_EXTS = {"gz", "bz2", "xz", "zip"}

_FORMAT_MAP: dict[str, str] = {
    "csv": "csv",
    "tsv": "tsv",
    "tab": "tsv",
    "txt": "lines",
    "log": "lines",
    "list": "lines",
    "json": "json",
    "yml": "yaml",
    "yaml": "yaml",
    "xlsx": "excel",
    "xls": "excel",
    "pickle": "pickle",
    "pkl": "pickle",
    "rds": "rds",
    "rda": "rda",
    "rdata": "rda",
    "gmt": "gmt",
    "gmx": "gmx",
    "grp": "grp",
    "gct": "gct",
    "gaf": "gaf",
    "mtx": "mtx",
    "parquet": "parquet",
    "feather": "feather",
    "arrow": "feather",
    "h5": "hdf5",
    "hdf5": "hdf5",
    "bam": "bam",
    "sam": "sam",
    "cram": "cram",
    "vcf": "vcf",
    "bcf": "bcf",
    "gff": "gff",
    "gff3": "gff",
    "gtf": "gtf",
    "bed": "bed",
    "bigwig": "bigwig",
    "bw": "bigwig",
    "bigbed": "bigbed",
    "bb": "bigbed",
    "wig": "wig",
    "fasta": "fasta",
    "fa": "fasta",
    "fna": "fasta",
    "fastq": "fastq",
    "fq": "fastq",
    "obo": "obo",
    "maf": "maf",
    "pzfx": "pzfx",
}


def file_ext(path: str) -> str:
    """Get file extension(s), collapsing compound extensions."""
    name = os.path.basename(path)
    parts = name.split(".")
    if len(parts) <= 1:
        return ""
    exts = parts[1:]
    if len(exts) >= 2 and exts[-1].lower() in _COMPRESS_EXTS:
        return ".".join(exts[-2:]).lower()
    return exts[-1].lower()


def compress_ext(path: str) -> str | None:
    """Get compression extension, or None."""
    ext = os.path.basename(path).split(".")[-1].lower()
    if ext in _COMPRESS_EXTS:
        return ext
    return None


def base_ext(path: str) -> str:
    """Get the base (non-compression) file extension.

    For compound extensions like ``csv.gz``, returns ``csv``.
    For bare compression extensions like ``gz``, returns ``""``
    (no inner format known).
    For non-compressed extensions, returns the extension unchanged.
    """
    ext = file_ext(path)
    for ce in _COMPRESS_EXTS:
        if ext.endswith("." + ce):
            return ext[: -(len(ce) + 1)]
        if ext == ce:
            # Bare compression with no inner extension: format unknown.
            return ""
    return ext


def is_url(path: str) -> bool:
    """Check if a path is a URL."""
    return bool(re.match(r"^(https?|ftp)://", path))


def basename_sans_ext(path: str) -> str:
    """Get basename without any extensions."""
    name = os.path.basename(path)
    parts = name.split(".")
    return parts[0]


def init_dir(path: str) -> str:
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)
    return path


def decompress_file(path: str, dest: str | None = None) -> str:
    """Decompress a file, returning path to decompressed file."""
    ext = compress_ext(path)
    if ext is None:
        return path
    if dest is None:
        stem = path
        if path.endswith("." + ext):
            stem = path[: -(len(ext) + 1)]
        dest = stem
    openers = {"gz": gzip.open, "bz2": bz2.open, "xz": lzma.open}
    if ext == "zip":
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            zf.extract(names[0], os.path.dirname(dest))
            return os.path.join(os.path.dirname(dest), names[0])
    opener = openers.get(ext)
    if opener is None:
        raise ValueError(f"Unsupported compression: {ext!r}")
    with opener(path, "rb") as fin, open(dest, "wb") as fout:
        shutil.copyfileobj(fin, fout)
    return dest


def compress_file(path: str, ext: str = "gz") -> str:
    """Compress a file, returning path to compressed file."""
    dest = path + "." + ext
    openers = {"gz": gzip.open, "bz2": bz2.open, "xz": lzma.open}
    opener = openers.get(ext)
    if opener is None:
        raise ValueError(f"Unsupported compression: {ext!r}")
    with open(path, "rb") as fin, opener(dest, "wb") as fout:
        shutil.copyfileobj(fin, fout)
    return dest


@contextmanager
def local_or_remote_file(path: str) -> Generator[str]:
    """Context manager yielding a local file path.

    If path is a URL, downloads to a temp file and yields the temp path.
    If path is an S3 URI, downloads from S3 to a temp file.
    Otherwise yields the path directly.
    """
    if is_url(path):
        suffix = "." + file_ext(path).split(".")[0] if file_ext(path) else ""
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp_path = tmp.name
        try:
            urllib.request.urlretrieve(path, tmp_path)
            yield tmp_path
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    elif path.startswith("s3://"):
        from pipette._s3 import _s3_download  # noqa: PLC0415

        tmp_path = _s3_download(path)
        try:
            yield tmp_path
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    else:
        yield path
