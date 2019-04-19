class MakeSpreadsheet:
    """
    usage: zentool -r <repo> spreadsheet <spreadsheet_id> make

    Dump the epics from a ZenHub repo into a spreadsheet
    """

    @classmethod
    def configure(cls, subparsers):
        sync_parser = subparsers.add_parser('make')
        sync_parser.set_defaults(subcommand='make')

    def __init__(self, tools):
        self.tools = tools
        self.repo = None

    def run(self, args):
        self.repo = self.tools.combo.repo(args.repo_name)
        if self.tools.sheet.get_cell("A1"):
            raise RuntimeError("This spreadsheet appears to have content already. "
                               "Did you mean to run 'sync'?")
        self.tools.sheet.update_range(range_name="A1:B2",
                                      values=[
                                          ["Repo:", self.repo.full_name],
                                          ["Epic", "Description"]
                                      ])
        row_cursor = 3  # 1-based
        for epic in self.repo.epics():
            if epic.status == 'open':
                range_name = f"A{row_cursor}:B"
                self.tools.sheet.update_range(range_name=range_name,
                                              values=[[epic.number, epic.title]])
                row_cursor += 1
