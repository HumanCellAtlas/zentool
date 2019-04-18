from colored import fg, bg, attr


class SyncSpreadsheet:
    """
    usage: zentool -r <repo> spreadsheet <spreadsheet_id> sync

    Retrieve issue status for epics
    """

    REPO_HEADER_ROW = 2
    REPO_HEADING_RANGE = "C2:Z"
    DATA_START_ROW = 3  # all spreadsheet references are 1-based

    class RepoMap:

        class RepoMapEntry:
            def __init__(self, repo, column):
                self.column = column
                self.repo = repo

            def __str__(self):
                return f"column={self.column}, repo={self.repo.full_name}"

        def __init__(self):
            self.map = dict()
            self.next_available_column = 3

        def __str__(self):
            output = "RepoMap "
            for k, v in self.map.items():
                output += f"{k}=({v}) "
            return output

        def record(self, repo, column):
            entry = self.RepoMapEntry(repo=repo, column=column)
            self.map[repo.id] = entry
            self.next_available_column = max(self.next_available_column, column + 1)
            return entry

        def create_new(self, repo):
            column = self.next_available_column
            self.next_available_column += 1
            entry = self.record(repo=repo, column=column)
            return entry

        def get_by_repo_name(self, repo_name):
            for entry in self.map.values():
                if entry.repo.full_name == repo_name:
                    return entry
            return None

    @classmethod
    def configure(cls, subparsers):
        sync_parser = subparsers.add_parser('sync')
        sync_parser.set_defaults(subcommand='sync')

    def __init__(self, tools):
        self.tools = tools
        self.repo = None
        self.repo_map = self.RepoMap()

    @property
    def sheet(self):
        return self.tools.sheet

    def run(self, args):
        self.repo = self.tools.combo.repo(args.repo_name)
        self._check_sheet_matches_repo()
        self._read_repo_headings()
        self._process_rows()

    def _check_sheet_matches_repo(self):
        headings = self.sheet.get_range("A1:B2")
        assert headings[0][0] == 'Repo:', "Expected Cell A1 to contain the word 'Repo:'."
        assert headings[0][1] == self.repo.full_name, (
            f"Command line specified repo {self.repo.full_name} "
            f"but spreadsheet is for repo {headings[0][1]}.")
        assert headings[1][0] == 'Epic', "Expected cell A2 to contain the heading 'Epic'."
        assert headings[1][1] == 'Description', "Expected cell B2 to contain the heading 'Description'."

    def _read_repo_headings(self):
        cells = self.sheet.get_range(self.REPO_HEADING_RANGE)
        if len(cells) == 0:
            return
        row = cells[0]
        col_number = 2  # 0-based
        for repo_name in row:
            col_number += 1
            if not self.repo_map.get_by_repo_name(repo_name):
                repo = self.tools.combo.repo(repo_name)
                self.repo_map.record(repo, col_number)

    def _process_rows(self):
        row_number = self.DATA_START_ROW
        sheet_data = self.sheet.get_range(f"A{self.DATA_START_ROW}:Z9999")
        for row in sheet_data:
            self.RowProcessor(sync=self).process(row, row_number)
            row_number += 1

    class RowProcessor:

        @property
        def sheet(self):
            return self.sync.sheet

        def __init__(self, sync):
            self.sync = sync
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
            self.epic = self.sync.repo.epic(epic_number)
            print(self.epic)
            cell_desc_addr = self.sync.tools.cell_addr(row=self.row_number, col=2)
            self.sheet.update_range(range_name=cell_desc_addr, values=[[self.epic.title]])

        def _find_or_create_column_for_repo(self, repo):
            map_entry = self.sync.repo_map.get_by_repo_name(repo.full_name)
            if map_entry:
                print(f"\t\t{repo.full_name} = column {map_entry.column}")
            else:
                map_entry = self.sync.repo_map.create_new(repo)
                print(f"\t\tassigning column {map_entry.column} to {repo.full_name}")
                header_addr = self.sync.tools.cell_addr(col=map_entry.column, row=2)
                self.sheet.update_range(header_addr, [[repo.full_name]])
            return map_entry

        def _insert_or_update_issue(self, issue, map_entry):
            cell_contents = self.row[map_entry.column - 1] if map_entry.column <= len(self.row) else None
            print(f"\t\tcontents = {cell_contents}")
            if not cell_contents:
                cell_addr = self.sync.tools.cell_addr(col=map_entry.column, row=self.row_number)
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
