import os
import sys


from lib.google_sheet import GoogleSheet
from .make_spreadsheet import MakeSpreadsheet
from .sync_spreadsheet import SyncSpreadsheet
from .issue_creator import IssueCreator


class SpreadsheetTools:

    @classmethod
    def configure(cls, subparsers):
        spreadsheet_parser = subparsers.add_parser('spreadsheet',
                                                   description="Spreadsheet manipulation tools")
        spreadsheet_parser.set_defaults(command='spreadsheet')
        spreadsheet_parser.add_argument('spreadsheet_id', type=str)
        subparsers = spreadsheet_parser.add_subparsers()

        MakeSpreadsheet.configure(subparsers)
        SyncSpreadsheet.configure(subparsers)
        IssueCreator.configure(subparsers)

    def __init__(self, combo):
        self.combo = combo
        self.sheet = None
        self._check_google_auth_is_configured()

    def run(self, args):
        self.sheet = GoogleSheet(args.spreadsheet_id)
        if args.subcommand == 'make':
            MakeSpreadsheet(tools=self).run(args)
        elif args.subcommand == 'sync':
            SyncSpreadsheet(tools=self).run(args)
        elif args.subcommand == 'create-issues':
            IssueCreator(tools=self).run(args)

    def cell_addr(self, row, col):
        """
        row and col should be 1-based
        """
        return f"{self.column_number_to_letter(col)}{row}"

    @staticmethod
    def column_number_to_letter(column_number):
        """
        column_number should be 1-based
        """
        return chr(65 + column_number - 1)

    @staticmethod
    def _check_google_auth_is_configured():
        if not os.path.exists('credentials.json'):
            sys.stderr.write("\nYou need to get credentials for accessing the Google Sheets API.\n"
                             "Go to https://developers.google.com/sheets/api/quickstart/python\n"
                             "click [ENABLE THE GOOGLE SHEETS API], then in the resulting dialog\n"
                             "click [DOWNLOAD CLIENT CONFIGURATION]\n"
                             "and save the file credentials.json to your working directory.\n\n")
            exit(1)
