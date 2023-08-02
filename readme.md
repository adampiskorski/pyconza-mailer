# PyConZA Mailer

This is my version of a PyConZA mailer, which exists in order to work with a different stack, namely [Mailtrap](https://mailtrap.io), [jinja2](https://jinja.palletsprojects.com) and [MJML](https://mjml.io).

## Data flow

A mailing list is consumed via a Google drive sheet, which is compared against a do not mail sheet, and only email addresses that are not on the do no mail list or are not already emailed.
The valid emails are then sent with the given template and context using Mailtrap.

## Templates

Templates are created using the MJML markup language, and Jinja2. The templates are converted to HTML by using the free [MJML API](https://mjml.io/api/documentation/), in order to avoid a nodejs dependency to the project.

There are 3 phases to a template:

1.  Pre-MJML conversion
    - These are templates that are to be rendered by Jinja2, with the intent of composing with base templates and enabling includes and macros, but with no personalization (such as names). Those parts of the templates wrapped with `{% raw %}` and `{% endraw %}`.
    - It is necessary to end up with a single file for the next MJML conversion step, as the MJML converter needs the entire MJML template in one file.
    - These templates are stored in the `pre_mjml` directory.
2.  MJML conversion
    - These are single file MJML templates, that ready to be converted to HTML, and have Jinja2 templating syntax for personalization.
    - These templates are stored in the `mjml` directory.
3.  Post-MJML conversion
    - These are HTML files, directly returned by the MJML to HTML conversion, and are ready for one more round of Jinja2 processing to personalize the emails, before being sent.
    - These templates are stored in the `html` directory.

## Plain text templates

Plain text templates must be provided as a fallback in case the user's email client does not support HTML emails.

This pipeline is much simpler, where all plain text templates are stored in the `txt` directory, and rendered and sent directly from there.

## Images

Media files such as images can be sent inline, by saving them in the `media` directory, and referring to them by pre-fixing their filenames with `cid:`.
For example: `src="cid:welcome.png"`

This app will then automatically find the all filenames referred to in the template prefixed with `cid:` and attach the file with the matching filename in the `media` directory

## Environmental variables

- SENDING_EMAIL: Email address that you will be sending from.
- SENDING_NAME: Human readable name representing the sender.
- SHEET_KEY_TO_EMAIL: Key for Google sheet (can be found in URL) that contains all emails to send to
- SHEET_KEY_TO_SKIP: Key for Google sheet (can be found in URL) that contains all emails to skip
- SHEET_KEY_UNSUBSCRIBED: Key for Google sheet (can be found in URL) that contains all emails to also skip due to unsubscription

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

- MAILTRAP_TOKEN: Token for Mailtrap

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
