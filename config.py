"""Settings file, where default settings and environment variables are defined."""

from pydantic import BaseModel
from pydantic.networks import EmailStr, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleKey(BaseModel):
    """Represent a google JSON Key."""

    project_id: str
    private_key_id: str
    private_key: str
    client_email: EmailStr
    client_id: str
    client_x509_cert_url: HttpUrl


class Settings(BaseSettings):
    """All settings."""

    mailtrap_host: str = "send.api.mailtrap.io"
    mailtrap_token: str
    mjml_endpoint: HttpUrl = HttpUrl("https://api.mjml.io/v1/render")
    mjml_app_id: str
    mjml_secret_key: str
    google_key: GoogleKey
    pre_mjml_path: str = "templates/pre_mjml/"
    mjml_path: str = "templates/mjml/"
    html_path: str = "templates/html/"
    txt_path: str = "templates/txt/"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="__"
    )


settings = Settings()
