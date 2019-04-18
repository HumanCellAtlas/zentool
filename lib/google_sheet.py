import os.path

import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GoogleSheet:

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.creds = None
        self._authenticate()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.sheets = self.service.spreadsheets()

    def get_range(self, range_name):
        result = self.sheets.values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        return result.get('values', [])

    def get_cell(self, address):
        result = self.sheets.values().get(spreadsheetId=self.spreadsheet_id, range=address).execute()
        values = result.get('values', [])
        return values[0][0] if values else None

    def update_range(self, range_name, values):
        """
        :param range_name: string, e.g. "H39", "H39:J42", or "Sheet Name!A1:B5"
        :param values: an list of lists
        """
        self.sheets.values().update(spreadsheetId=self.spreadsheet_id,
                                    range=range_name,
                                    valueInputOption='USER_ENTERED',
                                    body={'values': values}
                                    ).execute()

    def color_cell(self, rownum, colnum, red, green, blue):
        data = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "startRowIndex": rownum,
                            "endRowIndex": rownum+1,
                            "startColumnIndex": colnum,
                            "endColumnIndex": colnum+1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": "%.2f" % (red / 255),
                                    "green": "%.2f" % (green / 255),
                                    "blue": "%.2f" % (blue / 255)
                                },
                            },
                        },
                        "fields": "userEnteredFormat(backgroundColor)"
                    }
                }
            ]
        }
        self.sheets.batchUpdate(spreadsheetId=self.spreadsheet_id, body=data).execute()

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

