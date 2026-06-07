"""S3 (AWS) file support utilities."""

import os
import tempfile


def _is_s3_uri(path: str) -> bool:
    """Check if a path is an S3 URI.

    Parameters
    ----------
    path : str
        Path to check.

    Returns
    -------
    bool
        True if path starts with ``s3://``.
    """
    return path.startswith("s3://")


def _s3_parse_uri(uri: str) -> tuple[str, str]:
    """Parse an S3 URI into bucket and key.

    Parameters
    ----------
    uri : str
        S3 URI in the form ``s3://bucket/key``.

    Returns
    -------
    tuple of str
        (bucket, key) pair.
    """
    without_scheme = uri[len("s3://") :]
    bucket, _, key = without_scheme.partition("/")
    return bucket, key


def _s3_download(uri: str, *, quiet: bool = False) -> str:
    """Download an S3 object to a local temp file.

    Parameters
    ----------
    uri : str
        S3 URI to download.
    quiet : bool
        Suppress messages.

    Returns
    -------
    str
        Path to the downloaded temp file.
    """
    try:
        import boto3  # noqa: PLC0415
    except ImportError as err:
        msg = "boto3 is required for S3 support. Install it with: pip install boto3"
        raise ImportError(msg) from err
    bucket, key = _s3_parse_uri(uri)
    suffix = os.path.splitext(key)[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = tmp.name
    if not quiet:
        print(f"Downloading {uri}")
    boto3.client("s3").download_file(bucket, key, tmp_path)
    return tmp_path


def _s3_upload(local_path: str, uri: str, *, quiet: bool = False) -> str:
    """Upload a local file to S3.

    Parameters
    ----------
    local_path : str
        Local file to upload.
    uri : str
        Destination S3 URI.
    quiet : bool
        Suppress messages.

    Returns
    -------
    str
        The S3 URI.
    """
    try:
        import boto3  # noqa: PLC0415
    except ImportError as err:
        msg = "boto3 is required for S3 support. Install it with: pip install boto3"
        raise ImportError(msg) from err
    bucket, key = _s3_parse_uri(uri)
    if not quiet:
        print(f"Uploading to {uri}")
    boto3.client("s3").upload_file(local_path, bucket, key)
    return uri
