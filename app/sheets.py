"""Business logic for Google Sheets and preparing email addresses."""

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


class Email(BaseModel):
    """Represents an email address and its associated name, if provided."""

    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None


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
    emails: list[Email] = []
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
