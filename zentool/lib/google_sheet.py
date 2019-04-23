import os.path

import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from .sheet_range import SheetRange


class GoogleSheet:

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.creds = None
        self._authenticate()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.sheets = self.service.spreadsheets()

    def get_cells(self, range_name):
        result = self.sheets.values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        return result.get('values', [])

    def get_cell(self, address):
        values = self.get_cells(address)
        return values[0][0] if values else None

    def update_range(self, cells: SheetRange):
        body = {
            'requests': [
                {
                    'updateCells': {
                        'range': cells.to_google_grid_range(),
                        'fields': "*",
                        'rows': cells.to_google_rows()
                    }
                }
            ]
        }
        request = self.sheets.batchUpdate(spreadsheetId=self.spreadsheet_id, body=body)
        return request.execute()

    def _authenticate(self):
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

