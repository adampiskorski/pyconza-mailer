"""All conversion of MJML to HTML is done here."""

from pathlib import Path

import httpx

from mailer.config import settings
from mailer.helpers import get_html_path, get_mjml_path, read_file, write_file


class MJMLError(Exception):
    """Exception raised when the MJML API render endpoint returns an error."""

    def __init__(self, errors: list[str]):
        """Initialize the exception.

        Args:
            errors: list of errors returned by the MJML API render endpoint
        """
        self.message = f"The following errors occurred while rendering MJML: {errors}"
        super().__init__(self.message)


def _render_mjml_to_html(mjml: str) -> str:
    """Convert a given MJML string to HTML.

    Done using the MJML API render endpoint.

    Args:
        mjml: MJML to render

    Returns:
        The rendered HTML.

    Raises:
        httpx.HTTPStatusError: If there is an error with the HTTP request to the MJML API render endpoint.
        MJMLError: If there is an error with the rendering of the MJML itself.
    """
    payload = {"mjml": mjml}
    r = httpx.post(
        str(settings.mjml_endpoint),
        auth=(settings.mjml_app_id, settings.mjml_secret_key),
        json=payload,
    )
    r.raise_for_status()
    data = r.json()
    if errors := data.get("errors"):
        raise MJMLError(errors)
    return data["html"]


def convert_file(path: str):
    """Convert an MJML file to an HTML one.

    Args:
        path: path, relative to `templates/mjml/ directory`, to an MJML file

    Side effects:
        Saves output HTML to a file with the same path, but with an html extension, in the `templates/html/` directory.
    """
    full_mjml_path = get_mjml_path() / path
    mjml = read_file(full_mjml_path)
    html = _render_mjml_to_html(mjml)
    new_path = Path(path).with_suffix(".html")
    full_html_path = get_html_path() / new_path
    write_file(full_html_path, html)
