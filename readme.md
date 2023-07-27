# PyConZA Mailer

This is my version of a PyConZA mailer, which exists in order to work with a different stack, namely [Mailtrap](https://mailtrap.io), [jinja2](https://jinja.palletsprojects.com) and [MJML](https://mjml.io).

## Data flow

A mailing list is consumed via a Google drive sheet, which is compared against a do not mail sheet, and only email addresses that are not on the do no mail list or are not already emailed.
The valid emails are then sent with the given template and context using Mailtrap.

## Templates

Templates are created using the MJML markup language, and Jinja2. The templates are converted to HTML by using the free [MJML API](https://mjml.io/api/documentation/), in order to avoid a nodejs dependency to the project.

## Environmental variables

### Overridable defaults:

- MAILTRAP_HOST: Host identifier for Mailtrap
- MJML_ENDPOINT: URL for MJML API

### Secrets.

Put all secret environmental variables in a file called `.env` (which is ignored by git), or in your environment.

The following environmental variables represent the json key file of a Google service account:

- GOOGLE_KEY\_\_PROJECT_ID: `project_id`
- GOOGLE_KEY\_\_PRIVATE_KEY_ID: `private_key_id`
- GOOGLE_KEY\_\_PRIVATE_KEY: `private_key`
- GOOGLE_KEY\_\_CLIENT_EMAIL: `client_email`
- GOOGLE_KEY\_\_CLIENT_ID: `client_id`
- GOOGLE_KEY\_\_CLIENT_X509_CERT_URL: `client_x509_cert_url`

The following environmental variables represents Mailtrap and MJML secrets

- MAILTRAP_TOKEN: Token for Mailtrap

- MJML_APP_ID: MJML public API App ID (username)
- MJML_SECRET_KEY: MJML public API Secret key (password)
