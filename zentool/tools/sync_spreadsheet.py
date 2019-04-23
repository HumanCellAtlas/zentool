from colored import fg, bg, attr

from .spreadsheet_processor import SpreadsheetProcessor
from ..lib.sheet_range import SheetRange


class SyncSpreadsheet:
    """
    usage: zentool -r <repo> spreadsheet <spreadsheet_id> sync

    Retrieve issue status for epics
    """

    @classmethod
    def configure(cls, subparsers):
        sync_parser = subparsers.add_parser('sync')
        sync_parser.set_defaults(subcommand='sync')
        sync_parser.add_argument('epic_id', type=str, nargs='?')

    def __init__(self, tools):
        self.tools = tools

    def run(self, args):
        SpreadsheetProcessor(tools=self.tools, row_processor_class=self.SyncRowIssues).run(args)

    class SyncRowIssues:

        @property
        def sheet(self):
            return self.sheet_processor.sheet

        def __init__(self, sheet_processor):
            self.sheet_processor = sheet_processor
            self.row = None
            self.row_number = None
            self.epic = None
            self.header_range = SheetRange()
            self.row_range = SheetRange()

        def process(self, row, row_number):
            self.row = row
            self.row_number = row_number
            self._find_and_update_epic(epic_number=row[0])
            for issue in self.epic.issues():
                print(f"\t{issue}")
                map_entry = self._find_or_create_column_for_repo(issue.repo)
                self._update_issue_in_sheet(issue, map_entry)
            if not self.header_range.is_empty:
                self.sheet.update_range(self.header_range)
            if not self.row_range.is_empty:
                self.sheet.update_range(self.row_range)

        def _find_and_update_epic(self, epic_number):
            self.epic = self.sheet_processor.repo.epic(epic_number)
            print(self.epic)
            self.row_range['B', self.row_number] = self.epic.title

        def _find_or_create_column_for_repo(self, repo):
            map_entry = self.sheet_processor.repo_map.get_by_repo_name(repo.full_name)
            if map_entry:
                print(f"\t\t{repo.full_name} = column {map_entry.column}")
            else:
                map_entry = self.sheet_processor.repo_map.create_new(repo)
                print(f"\t\tassigning column {map_entry.column} to {repo.full_name}")
                column_letter = self.sheet_processor.tools.column_number_to_letter(map_entry.column)
                self.header_range[column_letter, 2] = repo.full_name
            return map_entry

        def _update_issue_in_sheet(self, issue, map_entry):
            colname = self.sheet_processor.tools.column_number_to_letter(map_entry.column)
            link_to_issue = '=HYPERLINK("https://github.com/{repo}/issues/{issue}","{issue}")'.format(
                repo=issue.repo.full_name, issue=issue.number)
            self.row_range[colname, self.row_number] = link_to_issue

            default_colors = {'red': 255, 'green': 255, 'blue': 200}
            state_to_colors_map = {
                'closed': {'red': 200, 'green': 255, 'blue': 200}
            }
            color = state_to_colors_map.get(issue.status, default_colors)

            self.row_range[colname, self.row_number].bg = color
