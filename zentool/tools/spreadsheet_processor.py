from .repo_map import RepoMap


class SpreadsheetProcessor:
    """
    Iterate through spreadsheet rows, calling the provided row processor
    """

    REPO_HEADER_ROW = 2
    REPO_HEADING_RANGE = "C2:Z"
    DATA_START_ROW = 3  # all spreadsheet references are 1-based

    def __init__(self, tools, row_processor_class):
        self.tools = tools
        self.repo = None
        self.repo_map = RepoMap()
        self.row_processor_class = row_processor_class

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
            self.row_processor_class(sheet_processor=self).process(row, row_number)
            row_number += 1
