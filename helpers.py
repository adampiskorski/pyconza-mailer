"""Helper functions common to all modules."""

from pathlib import Path, PosixPath


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
