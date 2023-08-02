"""Interface for the mailer app."""

from pathlib import Path

import fire
from rich import pretty, traceback
from rich.console import Console
from rich.progress import track
from rich.table import Table

from app.config import settings
from app.mjml import convert_file
from app.send import EmailGenerator
from app.sheets import get_all_emails_to_send
from app.templating import render_pre_mjml_file_to_mjml_file

pretty.install()
traceback.install(show_locals=True)


console = Console()


class Interface:
    """User interface through fire."""

    def __html_text_templates_from_name(self, name: str) -> tuple[Path, Path]:
        """Return the HTML and plain text templates for the given base file name.

        Args:
            name: Base file name of the template.

        Returns:
            A tuple containing the HTML and plain text templates for the given name.

        Raises:
            ValueError: If the template name includes a file extension.
        """
        template = Path(name)
        if template.suffix:
            raise ValueError("Template name should not include file extension.")
        html_template = template.with_suffix(".html")
        txt_template = template.with_suffix(".txt")
        return html_template, txt_template

    def __get_all_emails_to_send(self) -> list[tuple[str, str]]:
        """Return all the emails to send.

        Returns:
            List of tuples of recipients, where the first item is the email and the second their full name.
        """
        with console.status("[bold green]Fetching emails to send..."):
            emails, report = get_all_emails_to_send()

        table = Table(title="Emails to send")

        table.add_column("Total to send")
        table.add_column("Total unsubscribed")
        table.add_column("Total skipped")

        table.add_row(
            str(len(emails)),
            str(report.total_unsubscribed),
            str(report.total_skipped),
        )

        console.print(table)

        return emails

    def render_pre_mjml(self, template: str):
        """Render a pre-MJML template to the MJML folder, ready to be converted to HTML.

        Args:
            template: Path of the template file relative to the `pre_mjml` directory to render
        """
        with console.status(f"[bold green]Rendering `{template}`..."):
            render_pre_mjml_file_to_mjml_file(template)
        console.print(f"Rendered pre-MJML template `{template}`.", style="bold green")

    def render_mjml(self, template: str):
        """Render an MJML template to the HTML folder.

        Args:
            template: Path of the template file relative to the `mjml` directory to render
        """
        with console.status(f"[bold green]Rendering `{template}`..."):
            convert_file(template)
        console.print(f"Rendered MJML template `{template}` to HTML.", style="bold green")

    def full_render(self, template: str):
        """Render a pre-MJML template to the MJML folder, then to the HTML folder.

        Args:
            template: Path of the template file relative to the `pre_mjml` directory to render
        """
        self.render_pre_mjml(template)
        self.render_mjml(template)

    def send_template(
        self,
        template: str,
        subject: str,
        category: str = "Misc",
        dry_run: bool = False,
        test_server: bool = False,
    ):
        """Send the given email template to all recipients in the configured sheet.

        Unsubscribe and skipped email addresses are not sent to.

        Args:
            template: Common part of filename shared between txt and HTML templates.
            subject: Subject of the email. This can be a Jinja2 template string, with `name` available.
            category: Category of the email. Defaults to "Misc".
            dry_run: If True, do not send emails, just print what would be sent.
            test_server: If True, send emails to the Mailtrap test server instead of the real server.

        """
        if dry_run:
            mode_prefix = "[green]This is a dry run.[/]"
        elif test_server:
            mode_prefix = "[cyan]This is using the Mailtrap test server.[/]"
        else:
            mode_prefix = "[bold red]THIS WILL SEND EMAILS FOR REAL![/]"

        html_path, txt_path = self.__html_text_templates_from_name(template)
        recipients = self.__get_all_emails_to_send()

        answer = console.input(
            f"{mode_prefix} [red] Would you like to send these emails? "
            "Type [underline bold]yes[/] to proceed."
        )
        if answer != "yes":
            console.print("Aborting.", style="red")
            return

        with open(settings.sent_emails_file, "a") as f:
            sent_emails = []
            for sent_email in track(
                EmailGenerator(
                    recipients,
                    subject,
                    str(html_path),
                    str(txt_path),
                    category,
                    dry_run=dry_run,
                    test_server=test_server,
                ),
                description="[cyan]Sending emails",
            ):
                if not dry_run:
                    f.write(f"{template},{sent_email}\n")
                else:
                    sent_emails.append(sent_email)
        if dry_run:
            console.print("Would have sent emails to:")
            console.print(sent_emails)


if __name__ == "__main__":
    interface = Interface()
    fire.Fire(interface)
