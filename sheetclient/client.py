import typing as t

import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from sheetclient.paths import CLIENT_SECRET_FILE, CREDENTIAL_PATH
from sheetclient.values import APPLICATION_NAME


SCOPES = 'https://www.googleapis.com/auth/spreadsheets'


class GoogleSheetClient(object):
	_DISCOVERY_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'

	def __init__(self, meta_sheet_id: str):
		self._meta_sheet_id = meta_sheet_id

		self._credentials = self._get_credentials()

		self._service = discovery.build(
			'sheets',
			'v4',
			http = self._credentials.authorize(httplib2.Http()),
			discoveryServiceUrl = self._DISCOVERY_URL,
		)

	@classmethod
	def _get_credentials(cls) -> t.Any:
		store = Storage(CREDENTIAL_PATH)
		credentials = store.get()

		if not credentials or credentials.invalid:
			flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
			flow.user_agent = APPLICATION_NAME
			credentials = tools.run_flow(flow, store)

		return credentials

	@classmethod
	def _num_to_col_letters(cls, num: int) -> str:
		letters = ''

		while num:
			mod = (num - 1) % 26
			letters += chr(mod + 65)
			num = (num - 1) // 26

		return ''.join(reversed(letters))

	@classmethod
	def _coord_to_string(cls, column: int, row: int) -> str:
		return (
			cls._num_to_col_letters(
				column
			)
			+ str(row)
		)

	@classmethod
	def _range_name(cls, sheet_name: str, start_column: int, start_row: int, end_column: int, end_row: int) -> str:
		return '{}!{}:{}'.format(
			sheet_name,
			cls._coord_to_string(start_column, start_row),
			cls._coord_to_string(end_column, end_row),
		)

	def update_sheet(
		self,
		sheet_name: str,
		start_column: int,
		start_row: int,
		values: t.Sequence[t.Sequence[str]]
	) -> t.Any:
		update_values = {'values': values}

		_range = self._range_name(
			sheet_name = sheet_name,
			start_column = start_column,
			start_row = start_row,
			end_column = start_column + max(len(row) for row in values),
			end_row = start_row + len(values),
		)

		return (
			self._service
			.spreadsheets()
			.values()
			.update(
				spreadsheetId = self._meta_sheet_id,
				range = _range,
				valueInputOption = 'RAW',
				body = update_values,
			)
			.execute()
		)

	def read_sheet(
		self,
		sheet_name: str,
		start_column: int,
		start_row: int,
		end_column: int,
		end_row: int,
		major_dimension: str = 'ROWS',
	) -> t.List[t.List[str]]:
		_range = self._range_name(
			sheet_name = sheet_name,
			start_column = start_column,
			start_row = start_row,
			end_column = end_column,
			end_row = end_row,
		)

		vs = (
			self._service
			.spreadsheets()
			.values()
			.get(
				spreadsheetId = self._meta_sheet_id,
				range = _range,
				majorDimension = major_dimension,
			)
			.execute()
		)

		try:
			return vs['values']
		except KeyError:
			return []