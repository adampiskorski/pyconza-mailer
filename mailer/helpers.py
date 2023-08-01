"""Helper functions common to all modules."""

from pathlib import Path, PosixPath

from mailer.config import settings


def get_mjml_path() -> Path:
    """Return the base path for the MJML templates directory.

    Returns:
        The base path for the MJML templates directory.
    """
    return Path(settings.mjml_path)


def get_html_path() -> Path:
    """Return the base path for the HTML templates directory.

    Returns:
        The base path for the HTML templates directory.
    """
    return Path(settings.html_path)


def get_pre_mjml_path() -> Path:
    """Return the base path for the pre-MJML templates directory.

    Returns:
        The base path for the pre-MJML templates directory.
    """
    return Path(settings.pre_mjml_path)


def get_txt_path() -> Path:
    """Return the base path for the TXT templates directory.

    Returns:
        The base path for the TXT templates directory.
    """
    return Path(settings.txt_path)


def get_media_path() -> Path:
    """Return the base path for the media directory.

    Returns:
        The base path for the media directory.
    """
    return Path(settings.media_path)


def read_file(path: Path | PosixPath) -> str:
    """Read the file at the given path and returns a string representation of it.

    Args:
        path: path to the file to read

    Returns:
        A string representation of the file at the given path.
    """
    with open(path) as file:
        return file.read()


def write_file(path: Path | PosixPath, content: str):
    """Write the given content to the file at the given path.

    Args:
        path: path to the file to write to
        content: content to write to the file
    """
    with open(path, "w") as file:
        file.write(content)
