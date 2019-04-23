from zentool.lib.sheet_range import SheetRange


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

        range = SheetRange()
        range['A', 1] = "Repo:"
        range['B', 1] = self.repo.full_name
        range['A', 2] = "Epic"
        range['B', 2] = "Description"
        # TODO: format these headings

        row_cursor = 3  # 1-based
        for epic in self.repo.epics():
            if epic.status == 'open':
                print(f"Epic: {epic.number}, {epic.title}")
                range['A', row_cursor] = epic.number
                range['B', row_cursor] = epic.title
                row_cursor += 1

        print("Updating spredsheet...")
        self.tools.sheet.update_range(range)
