"""Interface for the mailer app."""

from pathlib import Path

import fire
from rich import pretty, traceback
from rich.console import Console

from app.mjml import convert_file
from app.send import send_email
from app.templating import render_pre_mjml_file_to_mjml_file

pretty.install()
traceback.install(show_locals=True)


console = Console()


class Interface:
    """User interface through fire."""

    def render_pre_mjml(self, template: str):
        """Render a pre-MJML template to the MJML folder, ready to be converted to HTML.

        Args:
            template: Path of the template file relative to the `pre_mjml` directory to render
        """
        console.print(f"Rendering `{template}`...")
        render_pre_mjml_file_to_mjml_file(template)
        console.print(f"Rendered `{template}`.", style="green")

    def render_mjml(self, template: str):
        """Render an MJML template to the HTML folder.

        Args:
            template: Path of the template file relative to the `mjml` directory to render
        """
        console.print(f"Rendering `{template}`...")
        convert_file(template)
        console.print(f"Rendered `{template}`.", style="green")

    def send_email(
        self,
        recipient_email: str,
        recipient_name: str,
        subject: str,
        template_name: str,
        context: dict,
    ):
        """Send an email directly from the CLI.

        This is intended to be used for testing.

        Args:
            recipient_email: List of tuples of email addresses and names of recipients.
            recipient_name: Name of the recipient.
            subject: Subject of the email.
            template_name: Common part of filename shared between txt and HTML templates.
            context: Context to render the templates with.

        Raises:
            ValueError: If the template name includes a file extension.

        Example:
            python mailer.py send_email "junk@piskorski.me" "Adam Piskorski" "Welcome {{ name }}" "first_email" '{"name":"Adam Piskorski"}'
        """
        template = Path(template_name)
        if template.suffix:
            raise ValueError("Template name should not include file extension.")
        html_template = template.with_suffix(".html")
        txt_template = template.with_suffix(".txt")

        console.print(f"Sending email to {recipient_email}<{recipient_name}>...")
        console.print(f"Using subject `{subject}`...")
        console.print(f"Using templates`{html_template}` and `{txt_template}`...")
        console.print(f"Using context `{context}`...")

        send_email(
            [(recipient_email, recipient_name)],
            subject,
            str(html_template),
            str(txt_template),
            context,
        )
        console.print(f"Email sent to {recipient_name}.", style="green")


if __name__ == "__main__":
    fire.Fire(Interface)
