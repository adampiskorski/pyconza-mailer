"""Use Mailtrap to send emails."""

import re
from abc import ABC, abstractmethod
from base64 import b64encode
from collections.abc import Generator
from mimetypes import guess_type
from pathlib import Path

import httpx
from mailtrap import Address, Attachment, Disposition, Mail, MailtrapClient
from mailtrap.mail.base import BaseMail

from app.config import settings
from app.helpers import get_media_path
from app.templating import render_html_file, render_string, render_txt_file


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


class MailTrapClientABC(MailtrapClient, ABC):
    """Abstract class for sending emails with custom endpoints."""

    @abstractmethod
    def send(self, mail: BaseMail):
        """Send the given mail to the given inbox.

        Args:
            mail: Mail to send.
        """

    @property
    def base_url(self) -> str:
        """Return the base URL for the Mailtrap API.

        Returns:
            The base URL for the Mailtrap API.
        """
        return f"https://{self.api_host.rstrip('/')}:{self.api_port}"


class MailtrapTestingClient(MailTrapClientABC):
    """Mailtrap client that sends to the Mailtrap Testing API."""

    def send(self, mail: BaseMail):
        """Send the given mail to the given inbox.

        Args:
            mail: Mail to send.

        Raises:
            ValueError: If MAILTRAP_TEST_INBOX_ID is not set.
        """
        inbox_id = settings.mailtrap_test_inbox_id
        if not inbox_id:
            raise ValueError("MAILTRAP_TEST_INBOX_ID not set")
        self.api_host = "sandbox.api.mailtrap.io"
        url = f"{self.base_url}/api/send/{inbox_id}"
        response = httpx.post(url, headers=self.headers, json=mail.api_data, timeout=30)
        if response.status_code != httpx.codes.OK:
            self._handle_failed_response(response)


class MailtrapMarketingClient(MailTrapClientABC):
    """Mailtrap client that sends through the marketing channel."""

    def send(self, mail: BaseMail):
        """Send the given mail to the given inbox.

        Args:
            mail: Mail to send.

        Raises:
            ValueError: If MAILTRAP_TEST_INBOX_ID is not set.
        """
        self.api_host = "bulk.api.mailtrap.io"
        url = f"{self.base_url}/api/send"
        response = httpx.post(url, headers=self.headers, json=mail.api_data, timeout=30)
        if response.status_code != httpx.codes.OK:
            self._handle_failed_response(response)


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
    recipient_email: str,
    recipient_name: str,
    subject: str,
    html: str,
    txt: str,
    attachments: list[Attachment],
    category: str,
    test_server: bool = False,
):
    """Send an email using Mailtrap.

    Args:
        recipient_email: Email address of the recipient.
        recipient_name: Full name of the recipient.
        subject: Subject of the email.
        html: HTML body of the email.
        txt: Plain text body of the email.
        attachments: List of Mailtrap attachment objects.
        category: Category of the email.
        test_server: If True, send the email to the Mailtrap test server instead of the real server.
    """
    mail = Mail(
        sender=Address(email=settings.sending_email, name=settings.sending_name),
        to=[Address(email=recipient_email, name=recipient_name or None)],
        subject=subject,
        text=txt,
        html=html,
        attachments=attachments,
        category=category,
    )
    if test_server:
        client = MailtrapTestingClient(token=settings.mailtrap_test_token)
    else:
        client = MailtrapMarketingClient(token=settings.mailtrap_token)
    client.send(mail)


def send_emails(
    recipients: list[tuple[str, str]],
    subject: str,
    html_path: str,
    txt_path: str,
    category: str,
    dry_run: bool = False,
    test_server: bool = False,
) -> Generator[str, None, None]:
    """Send an email using Mailtrap to each recipient.

    All templates, including the subject, can include `name` as a template variable,
    which will be replaced with the recipient's full name.

    Args:
        recipients: List of tuples of recipients, where the first item is the email and the second their full name.
        subject: Subject of the email. This can be a Jinja2 template string.
        html_path: Path to the HTML template.
        txt_path: Path to the Plain text template.
        category: Category of the email.
        dry_run: Whether to actually send the emails or not.
        test_server: If True, send emails to the Mailtrap test server instead of the real server.

    Yields:
        Each email address that gets sent to.
    """
    html_for_cid = render_html_file(html_path, {"name": "John Doe"})
    attachments = create_all_attachments(html_for_cid)
    for email, name in recipients:
        if not dry_run:
            context = {"name": name}
            subject = render_string(subject, context)
            html = render_html_file(html_path, context)
            txt = render_txt_file(txt_path, context)
            send_email(
                email,
                name,
                subject,
                html,
                txt,
                attachments,
                category,
                test_server=test_server,
            )
        yield email


class EmailGenerator:
    """Generator Wrapper to allow for better progress indication."""

    def __init__(
        self,
        recipients: list[tuple[str, str]],
        subject: str,
        html_path: str,
        txt_path: str,
        category: str,
        dry_run: bool = False,
        test_server: bool = False,
    ):
        """Initialize the generator with the same signature as `send_emails`.

        Args:
            recipients: List of tuples of recipients, where the first item is the email and the second their full name.
            subject: Subject of the email. This can be a Jinja2 template string.
            html_path: Path to the HTML template.
            txt_path: Path to the Plain text template.
            category: Category of the email.
            dry_run: Whether to actually send the emails or not.
            test_server: If True, send emails to the Mailtrap test server instead of the real server.
        """
        self.recipients = recipients
        self.subject = subject
        self.html_path = html_path
        self.txt_path = txt_path
        self.category = category
        self.dry_run = dry_run
        self.test_server = test_server

    def __iter__(self):
        """Return the generator for `send_emails`.

        Returns:
            The `send_emails` generator.
        """
        return send_emails(
            self.recipients,
            self.subject,
            self.html_path,
            self.txt_path,
            self.category,
            dry_run=self.dry_run,
            test_server=self.test_server,
        )

    def __len__(self):
        """Return the length of the recipients list."""
        return len(self.recipients)
