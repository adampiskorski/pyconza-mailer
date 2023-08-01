"""Use Mailtrap to send emails."""

import re
from base64 import b64encode
from mimetypes import guess_type
from pathlib import Path

from mailtrap import Address, Attachment, Disposition, Mail, MailtrapClient

from mailer.config import settings
from mailer.helpers import get_media_path
from mailer.templating import render_html_file, render_txt_file


class MimeTypeError(Exception):
    """Exception raised if a filenames mimetype could not be found."""

    def __init__(self, filename: str):
        """Initialize the exception.

        Args:
            filename: Filename for which the mimetype could not be found.
        """
        self.message = f"Could not find mimetype for {filename}"
        super().__init__(self.message)


class CidFileNotFoundError(Exception):
    """Exception raised if a CID file could not be found."""

    def __init__(self, filename: str):
        """Initialize the exception.

        Args:
            filename: Filename for which the CID file could not be found.
        """
        self.message = f"Could not find CID file for {filename}"
        super().__init__(self.message)


def get_all_cid_filenames(html: str) -> set[str]:
    """Return all the CID files in the given HTML.

    Args:
        html: HTML to search for CID files.

    Returns:
        A set of all the CID files in the given HTML.
    """
    pattern = r"cid:([\w\.-_]+.[\w\.-_]+)"
    matches = re.findall(pattern, html)
    return set(matches)


def get_media_file_path(filename: str) -> Path:
    """Return the path to the media file with the given filename.

    Args:
        filename: Filename of the media file.

    Returns:
        The path to the media file with the given filename.

    Raises:
        CidFileNotFoundError: If the media file could not be found.
    """
    path = get_media_path() / filename
    if not path.exists():
        raise CidFileNotFoundError(str(path))
    return path


def get_mime_type(path: Path) -> str:
    """Return the mimetype for the given path.

    Args:
        path: Path for which to find the mimetype.

    Returns:
        The mimetype for the given path.

    Raises:
        MimeTypeError: If the mimetype could not be found.
    """
    mimetype = guess_type(path)[0]
    if mimetype is None:
        raise MimeTypeError(str(path))
    return mimetype


def create_all_attachments(html: str) -> list[Attachment]:
    """Find all references to CID files in the given HTML and attach those files.

    Args:
        html: HTML string to search for CID files.

    Returns:
        A list of all the Mailtrap attachment objects to be added to the email.
    """
    cid_filenames = get_all_cid_filenames(html)
    attachments = []
    for filename in cid_filenames:
        path = get_media_file_path(filename)
        mimetype = get_mime_type(path)
        attachments.append(
            Attachment(
                content=b64encode(path.read_bytes()),
                filename=filename,
                disposition=Disposition.INLINE,
                mimetype=mimetype,
                content_id=filename,
            )
        )
    return attachments


def send_email(
    recipients: list[str],
    subject: str,
    html_path: str,
    txt_path: str,
    context: dict,
    category: str = "Misc",
):
    """Send an email using Mailtrap.

    Args:
        recipients: Email addresses of the recipients.
        subject: Subject of the email.
        html_path: Path to the HTML template.
        txt_path: Path to the Plain text template.
        context: Context to be used in the templates.
        category: Category of the email. Defaults to "Misc".
    """
    html = render_html_file(html_path, context)
    txt = render_txt_file(txt_path, context)
    attachments = create_all_attachments(html)
    mail = Mail(
        sender=Address(settings.sending_email, settings.sending_name),
        to=[Address(email=to) for to in recipients],
        subject=subject,
        text=txt,
        html=html,
        attachments=attachments,
        category=category,
    )

    client = MailtrapClient(token=settings.mailtrap_token)
    client.send(mail)
