# PyConZA Mailer

This is my version of a PyConZA mailer, which exists in order to work with a different stack, namely [Mailtrap](https://mailtrap.io), [jinja2](https://jinja.palletsprojects.com) and [MJML](https://mjml.io).

## Installation

Python 3.11 and [poetry](https://python-poetry.org/) is required, with the latter only required for installing dependencies and running the Python environment, so if you are familiar with managing those things yourself, then you can skip poetry.

Run `poetry install` to install all dependencies.

You will need 3 Google sheets (described below), a Google service account with access to all those sheets, a Mailtrap token and an MJML token and ID (all of these have generous free tiers).

Then configure the environmental variables needed (see the _Environmental variables section_)

### Google sheets

A mailing list is consumed via a Google drive sheet, which is compared against an unsubscribe sheet, and a skip sheet, and only email addresses that are not on the latter two lists selected to be sent to.
The valid emails are then sent with the given template Mailtrap.
There are dry run and Mailtrap test server modes.

## Usage example

### Render template

Write your MJML template and put it in the `templates/pre_mjml` directory. You can use Jinja2 to compose your template, and the context variable `name` will be available containing the full name of the recipient, however it could be an empty string.

Then to render it to HTML and make it ready to be sent, run:

```sh
poetry run python mailer.py full_render example.mjml
```

Where `example.mjml` is the name of your template.

### Send emails

To send out an email with the html and plain text templates named `example` (no extension), with the subject `PyConZA 2023 is happening`, then run the following command.

```sh
poetry run python mailer.py send_template example "PyConZA 2023 is happening"
```

The subject can also be a Jinja2 template string, with context variable `name` will be available containing the full name of the recipient, however it could be an empty string.

You must have a plain text template and HTML template for all emails sent, and both templates must have the same name, except for their extensions (for example: `template_name.html`, `template_name.txt`).

## Operating modes

### Dry run

There is a dry run mode, enabled with the `--dry_run=True` flag, which does not send any emails to Mailtrap at all (not even to the testing server), does not save to the sent emails log, but does print out all of the emails that would have been sent to.

### Test server

There is a dry run mode, enabled with the `--test_server=True` flag, which sends all emails to the Mailtrap test server

### Production mode

If neither of the above flags are specified, then all emails are sent for real through the Mailtrap production server.
All emails that are sent in this mode, and only this mode are appended to the send emails log file (default file name is `send_emails.log`)

### Rate limit

Mailtrap has a limit on the number of emails that can be sent in an hour.
You can honor this rate limit by automatically spreading out the sending of emails with the `--hourly_rate=50` flag, where 50 is the number of emails that you would like to send over the period of an hour.

## Templates

Templates are created using the MJML markup language, and Jinja2. The templates are converted to HTML by using the free [MJML API](https://mjml.io/api/documentation/), in order to avoid a nodejs dependency to the project.

## Context variables

The context variable `name`, will be available to all templates, and it contains the full name of the recipient, however it could be an empty string.

### Rendering pipeline

There are 3 phases to a template:

1.  Pre-MJML conversion
    - These are templates that you actually work on, and that are rendered by Jinja2, with the intent of composing with base templates and enabling includes and macros, but with no personalization (such as names). Those parts of the templates wrapped with `{% raw %}` and `{% endraw %}`.
    - It is necessary to end up with a single file for the next MJML conversion step, as the MJML converter needs the entire MJML template in one file.
    - These templates are stored in the `pre_mjml` directory.
2.  MJML conversion
    - These are single file MJML templates, that ready to be converted to HTML, and have Jinja2 templating syntax for personalization.
    - These templates are stored in the `mjml` directory.
3.  Post-MJML conversion
    - These are HTML files, directly returned by the MJML to HTML conversion, and are ready for one more round of Jinja2 processing to personalize the emails, before being sent.
    - These templates are stored in the `html` directory.

### Plain text templates

Plain text templates must be provided as a fallback in case the user's email client does not support HTML emails.

This pipeline is much simpler, where all plain text templates are stored in the `txt` directory, and rendered and sent directly from there.

### Images

Media files such as images can be sent inline, by saving them in the `media` directory, and referring to them by pre-fixing their filenames with `cid:`.
For example: `src="cid:welcome.png"`

This app will then automatically find the all filenames referred to in the template prefixed with `cid:` and attach the file with the matching filename in the `media` directory

## Environmental variables

This project is configured via environmental variables. A `.env` (with that name) file is also supported and ignored for security reasons.
An example `.env` file, called `example.env` is included to help get you started, with all the settings needed to get the project going and more (Just replace the values with your own)

- SENDING_EMAIL: Email address that you will be sending from.
- SENDING_NAME: Human readable name representing the sender.

- SHEET_TO_EMAIL\_\_KEY: Key for Google sheet (can be found in URL) that contains all emails to send to
- SHEET_TO_SKIP\_\_KEY: Key for Google sheet (can be found in URL) that contains all emails to skip
- SHEET_UNSUBSCRIBED\_\_KEY: Key for Google sheet (can be found in URL) that contains all emails to also skip due to unsubscription

- MAILTRAP_TEST_INBOX_ID: Mailbox ID for your Mailtrap test inbox (Optional if you won't use the test server)

### Secrets

Put all secret environmental variables in a file called `.env` (which is ignored by git), or in your environment.

The following environmental variables represent the json key file of a Google service account:

- GOOGLE_KEY\_\_PROJECT_ID: `project_id`
- GOOGLE_KEY\_\_PRIVATE_KEY_ID: `private_key_id`
- GOOGLE_KEY\_\_PRIVATE_KEY: `private_key`
- GOOGLE_KEY\_\_CLIENT_EMAIL: `client_email`
- GOOGLE_KEY\_\_CLIENT_ID: `client_id`
- GOOGLE_KEY\_\_CLIENT_X509_CERT_URL: `client_x509_cert_url`

The following environmental variables represents Mailtrap secrets

- MAILTRAP_TOKEN: Token for the Mailtrap production server
- MAILTRAP_TEST_TOKEN=Token for the Mailtrap test server (Optional if you won't use the test server)

The following environmental variables represents MJML secrets

- MJML_APP_ID: MJML public API App ID (username)
- MJML_SECRET_KEY: MJML public API Secret key (password)

### Overridable defaults

- MJML_ENDPOINT: URL for MJML API (default: `https://api.mjml.io/v1/render`)
- PRE_MJML_PATH: Path where all pre-MJML templates are stored (default: `templates/pre_mjml/`)
- MJML_PATH: Path where all templates ready for MJML conversion to HTML are stored (default: `templates/mjml/`)
- HTML_PATH: Path where all HTML templates are stored (default: `templates/html/`)
- TXT_PATH: Path where all plain text templates are stored (default: `templates/txt/`)
- MEDIA_PATH: Path where all media such as images are stored (default: `media/`)
- MAILTRAP_TEST_INBOX_ID: The test mailbox used mailtrap (default: `None`)
- SHEET_TO_EMAIL\_\_EMAIL_HEADING: The email column heading for the to send sheet (default: `Email`)
- SHEET_TO_EMAIL\_\_FIRST_NAME_HEADING: The First name column heading for the to send sheet (default: `First name`)
- SHEET_TO_EMAIL\_\_LAST_NAME_HEADING: The Last name column heading for the to send sheet (default: `Surname`)
- SHEET_TO_SKIP\_\_EMAIL_HEADING: The email column heading for the to skip sheet (default: `Email`)
- SHEET_UNSUBSCRIBED\_\_EMAIL_HEADING: The email column heading for the unsubscribe sheet (default: `Email address`)
- SENT_EMAILS_FILE: File to log emails that have been sent for real (default: `sent_emails.log`)
