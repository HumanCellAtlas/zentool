from colored import fg, bg, attr

from .spreadsheet_processor import SpreadsheetProcessor
from ..lib.sheet_range import SheetRange


class IssueCreator:
    """
    usage: zentool -r <repo> spreadsheet <spreadsheet_id> create-issues

    Create an issue for every 🛠 in tracking spreadsheet.
    """

    @classmethod
    def configure(cls, subparsers):
        sync_parser = subparsers.add_parser('create-issues')
        sync_parser.set_defaults(subcommand='create-issues')
        sync_parser.add_argument('epic_id', type=str, nargs='?')

    def __init__(self, tools):
        self.tools = tools

    def run(self, args):
        SpreadsheetProcessor(tools=self.tools, row_processor_class=self.CreateRowIssues).run(args)

    class CreateRowIssues:

        @property
        def sheet(self):
            return self.sheet_processor.sheet

        def __init__(self, sheet_processor):
            self.sheet_processor = sheet_processor
            self.row = None
            self.row_number = None
            self.epic = None
            self.row_range = SheetRange()

        def process(self, row, row_number):
            self.row = row
            self.row_number = row_number
            self._find_and_update_epic(epic_number=row[0])
            import pdb; pdb.set_trace()
            for map_entry in self.sheet_processor.repo_map.map.values():
                try:
                    cell_value = self.row[map_entry.column - 1]
                except IndexError:
                    cell_value = None

                if cell_value == '🛠':
                    issue = map_entry.repo.create_issue(self.epic.title, self.epic.body)
                    print(f"\tCreated issue {issue}")
                    self.update_issue_in_sheet(issue, map_entry)
                    print("\tAdding issue to epic")
                    self.epic.add_issues([issue])

            if not self.row_range.is_empty:
                self.sheet.update_range(self.row_range)

        def _find_and_update_epic(self, epic_number):
            self.epic = self.sheet_processor.repo.epic(epic_number)
            print(self.epic)
            self.row_range['B', self.row_number] = self.epic.title

        def update_issue_in_sheet(self, issue, map_entry):
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
