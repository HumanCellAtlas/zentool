from colored import fg, bg, attr

from .spreadsheet_processor import SpreadsheetProcessor


class IssueCreator:
    """
    usage: zentool -r <repo> spreadsheet <spreadsheet_id> create-issues

    Create an issue for every 🛠 in tracking spreadsheet.
    """

    @classmethod
    def configure(cls, subparsers):
        sync_parser = subparsers.add_parser('create-issues')
        sync_parser.set_defaults(subcommand='create-issues')

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

        def process(self, row, row_number):
            self.row = row
            self.row_number = row_number
            self._find_and_update_epic(epic_number=row[0])

            for map_entry in self.sheet_processor.repo_map.map.values():
                try:
                    cell_value = self.row[map_entry.column - 1]
                except IndexError:
                    cell_value = None

                if cell_value == '🛠':
                    print(f"\tCreating issue in repo {map_entry.repo.full_name}")
                    issue = map_entry.repo.create_issue(self.epic.title, self.epic.body)

                    cell_addr = self.sheet_processor.tools.cell_addr(col=map_entry.column, row=self.row_number)
                    self._insert_link_to_issue(issue, cell_addr)
                    self._update_issue_status_color(issue, map_entry)
                    print("\tAdding issue to epic")
                    self.epic.add_issues([issue])

        def _find_and_update_epic(self, epic_number):
            self.epic = self.sheet_processor.repo.epic(epic_number)
            print(self.epic)
            cell_desc_addr = self.sheet_processor.tools.cell_addr(row=self.row_number, col=2)
            self.sheet.update_range(range_name=cell_desc_addr, values=[[self.epic.title]])

        def _insert_link_to_issue(self, issue, cell_addr):
            link_to_issue = '=HYPERLINK("https://github.com/{repo}/issues/{issue}","{issue}")'.format(
                repo=issue.repo.full_name, issue=issue.number)
            print(f"\t\t{fg('yellow')}updating {cell_addr} to {link_to_issue}{attr('reset')}")
            self.sheet.update_range(range_name=cell_addr, values=[[link_to_issue]])

        def _update_issue_status_color(self, issue, map_entry):
            print(f"\t\t{fg('yellow')}updating color{attr('reset')}")
            default_colors = {'red': 255, 'green': 255, 'blue': 200}
            state_to_colors_map = {
                'closed': {'red': 200, 'green': 255, 'blue': 200}
            }
            color = state_to_colors_map.get(issue.status, default_colors)
            self.sheet.color_cell(self.row_number - 1, map_entry.column - 1, **color)
