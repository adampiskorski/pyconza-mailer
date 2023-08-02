"""Business logic for Google Sheets and preparing email addresses."""

from dataclasses import dataclass
from typing import Annotated

import gspread
from gspread import Worksheet
from gspread.client import Client
from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator
from pydantic.networks import EmailStr

from app.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]


def to_lower(v: str) -> str:
    """Convert a string to lowercase.

    Args:
        v: String to convert to lowercase.

    Returns:
        The string converted to lowercase.
    """
    return v.lower()


class Email(BaseModel):
    """Represents an email address and its associated name, if provided."""

    email: Annotated[EmailStr, AfterValidator(to_lower)]
    first_name: str | None = None
    last_name: str | None = None

    @property
    def full_name(self) -> str:
        """Get the full name of the email object.

        Returns:
            A full name, or an empty string.
        """
        if self.first_name:
            if self.last_name:
                return f"{self.first_name} {self.last_name}"
            return self.first_name
        return self.last_name or ""


def unique_emails(v: list[Email]) -> list[Email]:
    """Validate that there are no duplicate email addresses.

    Will show which email address is duplicated.

    Args:
        v: List of Emails

    Returns:
        List of Emails
    """
    checked_emails: set[EmailStr] = set()
    for email in v:
        if email.email in checked_emails:
            raise ValueError(f"Duplicate email address: {email.email}")
        checked_emails.add(email.email)
    return v


class Emails(BaseModel):
    """Represents many email addresses and their associated names."""

    emails: Annotated[list[Email], AfterValidator(unique_emails)]

    def emails_to_set(self) -> set[EmailStr]:
        """Convert the list of emails to a set of email address literals.

        Returns:
            set: Set of email addresses literals.
        """
        return {email.email for email in self.emails}


@dataclass
class CompositionReport:
    """Represents a report of various modifications to a list of emails when it was composed."""

    total_unsubscribed: int
    total_skipped: int


def get_client() -> Client:
    """Get a gspread client.

    Returns:
        gspread client
    """
    creds = settings.google_key.serialize()
    return gspread.service_account_from_dict(creds)


def get_first_worksheet(key: str) -> Worksheet:
    """Get a the first gspread Worksheet that belongs to the Spreadsheet with the given key.

    Args:
        key: Key of the Spreadsheet that the Worksheet belongs to.

    Returns:
        gspread worksheet
    """
    client = get_client()
    sheet = client.open_by_key(key)
    return sheet.get_worksheet(0)


def get_all_emails_from_worksheet(
    worksheet: Worksheet, email_heading: str, name_headings: tuple[str, str] | None = None
) -> Emails:
    """Get all email addresses from a worksheet.

    Args:
        worksheet: Worksheet to get email addresses from.
        email_heading: Heading of the column that contains email addresses.
        name_headings: Tuple of first and last name headings, if available. Defaults to None.

    Returns:
        Emails: All email addresses from the worksheet.
    """
    list_of_dicts = worksheet.get_all_records()
    if email_heading not in list_of_dicts[0]:
        raise ValueError(
            f"Email heading '{email_heading}' not found in worksheet {worksheet}."
        )
    emails: list[Email] = []
    if name_headings:
        if name_headings[0] not in list_of_dicts[0]:
            raise ValueError(
                f"First name heading '{name_headings[0]}' not found in worksheet {worksheet}."
            )
        if name_headings[1] not in list_of_dicts[0]:
            raise ValueError(
                f"Last name heading '{name_headings[1]}' not found in worksheet {worksheet}."
            )
    if name_headings:
        emails.extend(
            Email(
                email=d[email_heading],
                first_name=d[name_headings[0]],
                last_name=d[name_headings[1]],
            )
            for d in list_of_dicts
        )
    else:
        emails.extend(Email(email=d[email_heading]) for d in list_of_dicts)
    return Emails(emails=emails)


def get_to_send_emails() -> Emails:
    """Get all email addresses to send.

    Returns:
        Emails: All email addresses to send.
    """
    worksheet = get_first_worksheet(settings.sheet_to_email.key)
    if (
        settings.sheet_to_email.first_name_heading
        and settings.sheet_to_email.last_name_heading
    ):
        name_tuple = (
            settings.sheet_to_email.first_name_heading,
            settings.sheet_to_email.last_name_heading,
        )
    else:
        name_tuple = None
    return get_all_emails_from_worksheet(
        worksheet, settings.sheet_to_email.email_heading, name_tuple
    )


def get_to_skip_emails() -> Emails:
    """Get all email addresses to skip.

    Returns:
        Emails: All email addresses to skip.
    """
    worksheet = get_first_worksheet(settings.sheet_to_skip.key)
    return get_all_emails_from_worksheet(worksheet, settings.sheet_to_skip.email_heading)


def get_unsubscribed_emails() -> Emails:
    """Get all email addresses to skip.

    Returns:
        Emails: All email addresses to skip.
    """
    worksheet = get_first_worksheet(settings.sheet_unsubscribed.key)
    return get_all_emails_from_worksheet(
        worksheet, settings.sheet_unsubscribed.email_heading
    )


def get_all_emails_to_send() -> tuple[list[tuple[str, str]], CompositionReport]:
    """Get all email addresses to send.

    Returns:
        Email tuples: List of tuples of recipients, where the first item is the email and the second their full name.
        CompositionReport: Report of various modifications to the list of emails when it was composed.
    """
    original: Emails = get_to_send_emails()
    to_skip: set[EmailStr] = get_to_skip_emails().emails_to_set()
    unsubscribed: set[EmailStr] = get_unsubscribed_emails().emails_to_set()
    to_send: list[tuple[str, str]] = []
    removed_skipped: int = 0
    removed_unsubscribed: int = 0
    for email in original.emails:
        if email.email in unsubscribed:
            removed_unsubscribed += 1
        elif email.email in to_skip:
            removed_skipped += 1
        else:
            to_send.append((str(email.email), email.full_name))
    report = CompositionReport(
        total_skipped=removed_skipped,
        total_unsubscribed=removed_unsubscribed,
    )
    return to_send, report
