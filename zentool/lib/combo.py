from github import Github
from .zenhub import ZenHub


class Combo:
    """
    Aggregate both GitHub and ZenHub functionality
    ZenHub is pretty weak and needs info from GitHub
    """

    def __init__(self, gh_token, zh_token):
        self.github = Github(login_or_token=gh_token)
        self.zenhub = ZenHub(api_token=zh_token)

    def repo(self, repo_full_name):
        return Combo.Repo(repo_full_name, self)

    class Repo:
        def __init__(self, repo_full_name_or_id, combo):
            self.combo = combo
            self.git = combo.github.get_repo(repo_full_name_or_id)
            self.zen = combo.zenhub.repository(repo_id=self.git.id)

        def __str__(self):
            return f"{self.__class__.__name__} {self.full_name}"

        def __repr__(self):
            return f"{self.__class__.__name__}[{self.id}]"

        @property
        def id(self):
            return self.git.id

        @property
        def full_name(self):
            return self.git.full_name

        def get_labeled_issues(self, labels):
            """
            Search for issues in GH repo
            """
            gh_labels = [self.git.get_label(label) for label in labels]
            return [Combo.Issue(repo=self, gh_issue=gh_issue) for gh_issue in self.git.get_issues(labels=gh_labels)]

        def create_issue(self, title, body):
            gh_issue = self.git.create_issue(title, body)
            return Combo.Issue(self, gh_issue=gh_issue)

        def issue(self, number):
            return Combo.Issue(number=number, repo=self)

        def epics(self):
            return [
                Combo.Epic(number=zh_epic.id, zh_epic=zh_epic, repo=self)
                for zh_epic in self.zen.epics()
            ]

        def epic(self, number):
            return Combo.Epic(number=number, repo=self)

        def board(self):
            data = self.combo.zenhub.get(f"/p1/repositories/{self.id}/board")
            return ZenHub.Board(data, repo=self)

    class Issue:
        def __init__(self, repo, number=None, gh_issue=None, zh_issue=None):
            if not number and not gh_issue and not zh_issue:
                raise RuntimeError("you must provide either number, gh_issue or zh_issue")
            self._number = number
            self.repo = repo
            self._gh_issue = gh_issue
            self._zh_issue = zh_issue
            self._id = id

        def __str__(self):
            return f"{self.__class__.__name__} " \
                   f"{self.repo.full_name}/{self.number} ({self.status}) \"{self.title}\""

        def __repr__(self):
            return f"{self.__class__.__name__} [{self.repo.id}/{self.id}]"

        @property
        def id(self):
            return self.gh_issue.id if self.gh_issue else self._id

        @property
        def number(self):
            return self.gh_issue.number if self._gh_issue else self.zh_issue.id if self._zh_issue else self._number

        @property
        def title(self):
            return self.gh_issue.title

        @property
        def status(self):
            return self.gh_issue.state

        @property
        def zh_issue(self):
            if not self._zh_issue:
                self._zh_issue = self.repo.zen.issue(self.number)
            return self._zh_issue

        @property
        def gh_issue(self):
            if not self._gh_issue:
                self._gh_issue = self.repo.git.get_issue(self.number)
            return self._gh_issue

    class Epic:
        def __init__(self, repo, number=None, zh_epic=None, gh_issue=None):
            self.repo = repo
            self._zh_epic = zh_epic
            self._gh_issue = gh_issue
            self.number = number

        def __str__(self):
            return f"{self.__class__.__name__} {self.repo.full_name}/{self.number} \"{self.title}\""

        def __repr__(self):
            return f"{self.__class__.__name__}[{self.repo.id}/{self.number}]"

        @property
        def zh_epic(self):
            if not self._zh_epic:
                self._zh_epic = self.repo.zen.epic(self.number)
            return self._zh_epic

        @property
        def gh_issue(self):
            if not self._gh_issue:
                self._gh_issue = self.repo.git.get_issue(int(self.number))
            return self._gh_issue

        @property
        def title(self):
            return self.gh_issue.title

        @property
        def body(self):
            return self.gh_issue.body

        @property
        def pipeline(self):
            return self.zh_epic.pipeline

        @property
        def status(self):
            return self.gh_issue.state

        def raw_issues(self):
            return self.zh_epic.raw_issues()

        def issues(self):
            return [
                self.repo.combo.repo(issue_data['repo_id']).issue(issue_data['issue_number'])
                for issue_data in self.zh_epic.raw_issues()
            ]

        def add_issues(self, issues):
            self.zh_epic.add_issues(issues)
