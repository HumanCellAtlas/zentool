from colored import fg, bg, attr

from .spreadsheet_processor import SpreadsheetProcessor


class SyncSpreadsheet:
    """
    usage: zentool -r <repo> spreadsheet <spreadsheet_id> sync

    Retrieve issue status for epics
    """

    @classmethod
    def configure(cls, subparsers):
        sync_parser = subparsers.add_parser('sync')
        sync_parser.set_defaults(subcommand='sync')

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

        def process(self, row, row_number):
            self.row = row
            self.row_number = row_number
            self._find_and_update_epic(epic_number=row[0])
            for issue in self.epic.issues():
                print(f"\t{issue}")
                map_entry = self._find_or_create_column_for_repo(issue.repo)
                self._insert_or_update_issue(issue, map_entry)
                self._update_issue_status_color(issue, map_entry)

        def _find_and_update_epic(self, epic_number):
            self.epic = self.sheet_processor.repo.epic(epic_number)
            print(self.epic)
            cell_desc_addr = self.sheet_processor.tools.cell_addr(row=self.row_number, col=2)
            self.sheet.update_range(range_name=cell_desc_addr, values=[[self.epic.title]])

        def _find_or_create_column_for_repo(self, repo):
            map_entry = self.sheet_processor.repo_map.get_by_repo_name(repo.full_name)
            if map_entry:
                print(f"\t\t{repo.full_name} = column {map_entry.column}")
            else:
                map_entry = self.sheet_processor.repo_map.create_new(repo)
                print(f"\t\tassigning column {map_entry.column} to {repo.full_name}")
                header_addr = self.sheet_processor.tools.cell_addr(col=map_entry.column, row=2)
                self.sheet.update_range(header_addr, [[repo.full_name]])
            return map_entry

        def _insert_or_update_issue(self, issue, map_entry):
            cell_contents = self.row[map_entry.column - 1] if map_entry.column <= len(self.row) else None
            print(f"\t\tcontents = {cell_contents}")
            if not cell_contents:
                cell_addr = self.sheet_processor.tools.cell_addr(col=map_entry.column, row=self.row_number)
                self._insert_link_to_issue(issue, cell_addr)

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
