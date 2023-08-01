"""Jinja2 template rendering functions."""

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.helpers import (
    get_html_path,
    get_mjml_path,
    get_pre_mjml_path,
    get_txt_path,
    write_file,
)


def get_pre_mjml_env() -> Environment:
    """Return the Jinja2 environment for the pre-MJML templates.

    Returns:
        The Jinja2 environment for the pre-MJML templates.
    """
    return Environment(
        loader=FileSystemLoader(get_pre_mjml_path()), autoescape=select_autoescape()
    )


def get_html_env() -> Environment:
    """Return the Jinja2 environment for the HTML templates.

    Returns:
        The Jinja2 environment for the HTML templates.
    """
    return Environment(
        loader=FileSystemLoader(get_html_path()), autoescape=select_autoescape()
    )


def get_txt_env() -> Environment:
    """Return the Jinja2 environment for the TXT templates.

    Returns:
        The Jinja2 environment for the TXT templates.
    """
    return Environment(
        loader=FileSystemLoader(get_txt_path()), autoescape=select_autoescape()
    )


def render_pre_mjml_file_to_mjml_file(path: str, context: dict | None = None):
    """Render a pre-MJML template to to the MJML folder, ready to be converted to HTML.

    Args:
        path: Path of the template file relative to the `pre_mjml` directory to render
        context: Context dictionary to render the template with. Defaults to None.
    """
    context = context or {}
    env = get_pre_mjml_env()
    template = env.get_template(path)
    rendered = template.render(**context)
    new_path = get_mjml_path() / path
    write_file(new_path, rendered)


def render_html_file(path: str, context: dict | None = None) -> str:
    """Render the given HTML template in the `html` directory to a string.

    Args:
        path: Path of the template file relative to the `html` directory to render
        context: Context dictionary to render the template with. Defaults to None.

    Returns:
        The rendered template as a string.
    """
    context = context or {}
    env = get_html_env()
    template = env.get_template(path)
    return template.render(**context)


def render_txt_file(path: str, context: dict | None = None) -> str:
    """Render the given Plain text template in the `txt` directory to a string.

    Args:
        path: Path of the template file relative to the `txt` directory to render
        context: Context dictionary to render the template with. Defaults to None.

    Returns:
        The rendered template as a string.
    """
    context = context or {}
    env = get_txt_env()
    template = env.get_template(path)
    return template.render(**context)
