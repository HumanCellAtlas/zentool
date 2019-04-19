class RepoMap:
    """
    Maintains a map of repo numbers to the repos and their spreadsheet columns
    """

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
