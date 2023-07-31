"""Jinja2 template rendering functions."""

from jinja2 import Environment, FileSystemLoader, select_autoescape

from helpers import get_mjml_path, write_file


def get_pre_mjml_env() -> Environment:
    """Return the Jinja2 environment for the pre-MJML templates.

    Returns:
        The Jinja2 environment for the pre-MJML templates.
    """
    return Environment(
        loader=FileSystemLoader("templates/pre_mjml"), autoescape=select_autoescape()
    )


def get_html_env() -> Environment:
    """Return the Jinja2 environment for the HTML templates.

    Returns:
        The Jinja2 environment for the HTML templates.
    """
    return Environment(
        loader=FileSystemLoader("templates/html"), autoescape=select_autoescape()
    )


def render_to_mjml_file(path: str, context: dict | None = None):
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
