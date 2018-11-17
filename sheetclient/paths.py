import os

from secretresources import paths

from sheetclient import values


SECRETS_PATH = paths.project_name_to_secret_dir(values.APPLICATION_NAME)

CLIENT_SECRET_FILE = os.path.join(
	SECRETS_PATH,
	'client_secret.json',
)

CREDENTIAL_PATH = os.path.join(
	SECRETS_PATH,
	'storage.json'
)
