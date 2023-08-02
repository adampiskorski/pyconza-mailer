"""Settings file, where default settings and environment variables are defined."""

from pydantic import BaseModel
from pydantic.networks import EmailStr, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleKey(BaseModel):
    """Represent a google JSON Key."""

    type: str = "service_account"  # noqa: A003
    project_id: str
    private_key_id: str
    private_key: str
    client_email: EmailStr
    client_id: str
    auth_uri: HttpUrl = HttpUrl("https://accounts.google.com/o/oauth2/auth")
    token_uri: HttpUrl = HttpUrl("https://oauth2.googleapis.com/token")
    auth_provider_x509_cert_url: HttpUrl = HttpUrl(
        "https://www.googleapis.com/oauth2/v1/certs"
    )
    client_x509_cert_url: HttpUrl

    def serialize(self) -> dict:
        """Serialize the key to a dictionary.

        Returns:
            dict: The serialized key.
        """
        d = self.model_dump()
        for key, value in d.items():
            d[key] = str(value)
        return d


class SheetToEmail(BaseModel):
    """Represent the Google sheet used to get email addresses of recipients."""

    key: str
    email_heading: str = "Email"
    first_name_heading: str | None = "First name"
    last_name_heading: str | None = "Surname"


class SheetToSkip(BaseModel):
    """Represent the Google sheet used to get email addresses of recipients to not email."""

    key: str
    email_heading: str = "Email"


class SheetUnsubscribed(BaseModel):
    """Represent the Google sheet used to get email addresses of recipients who wish to never be emailed."""

    key: str
    email_heading: str = "Email address"


class Settings(BaseSettings):
    """All settings."""

    sending_email: EmailStr
    sending_name: str
    mailtrap_token: str
    mailtrap_test_inbox_id: int | None = None
    sheet_to_email: SheetToEmail
    sheet_to_skip: SheetToSkip
    sheet_unsubscribed: SheetUnsubscribed
    mjml_endpoint: HttpUrl = HttpUrl("https://api.mjml.io/v1/render")
    mjml_app_id: str
    mjml_secret_key: str
    google_key: GoogleKey
    pre_mjml_path: str = "templates/pre_mjml/"
    mjml_path: str = "templates/mjml/"
    html_path: str = "templates/html/"
    txt_path: str = "templates/txt/"
    media_path: str = "media/"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__"
    )


settings = Settings()
