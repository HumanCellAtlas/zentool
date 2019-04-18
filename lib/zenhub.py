import json

import requests


class ZenHub:
    """
    Python binding for the ZenHub API described at https://github.com/ZenHubIO/API

                                                                            Issues
    GET    /p1/repositories/:repo_id/issues/:issue_number                       Get Issue Data
    GET    /p1/repositories/:repo_id/issues/:issue_number/events                Get Issue Events
    POST   /p1/repositories/:repo_id/issues/:issue_number/moves                 Move an Issue Between Pipelines
    PUT    /p1/repositories/:repo_id/issues/:issue_number/estimate              Set Issue Estimate
                                                                            Epics
    GET    /p1/repositories/:repo_id/epics                                      Get Epics for a Repository
    GET    /p1/repositories/:repo_id/epics/:epic_id                             Get Epic Data
    POST   /p1/repositories/:repo_id/epics/:issue_number/convert_to_issue       Convert an Epic to an Issue
    POST   /p1/repositories/:repo_id/issues/:issue_number/convert_to_epic       Convert an Issue to Epic
    POST   /p1/repositories/:repo_id/epics/:issue_number/update_issues          Add or Remove Issues from an Epic
                                                                            Board
    GET    /p1/repositories/:repo_id/board                                      Get Board Data for a Repository
                                                                            Milestones
    POST   /p1/repositories/:repo_id/milestones/:milestone_number/start_date    Set the Milestone Start Date
    GET    /p1/repositories/:repo_id/milestones/:milestone_number/start_date    Get the Milestone Start Date
                                                                            Dependencies
    GET    /p1/repositories/:repo_id/dependencies                               Get Dependencies for a Repository
    POST   /p1/dependencies                                                     Create a Dependency
    DELETE /p1/dependencies                                                     Remove a Dependency
                                                                            Release Reports
    POST   /p1/repositories/:repo_id/reports/release                            Create a Release Report
    GET    /p1/reports/release/:release_id                                      Get a Release Report
    GET    /p1/repositories/:repo_id/reports/releases                           Get Release Reports for a Repository
    PATCH  /p1/reports/release/:release_id                                      Edit a Release Report
    POST   /p1/reports/release/:release_id/repositories/:repo_id                Add Workspaces to a Release Report
    DELETE /p1/reports/release/:release_id/repositories/:repo_id                Remove Workspaces from a Release Report
                                                                            Release Report Issues
    GET    /p1/reports/release/:release_id/issues                               Get all the Issues in a Release Report
    PATCH  /p1/reports/release/:release_id/issues                               Add or Remove Issues from a Release Report
    """

    DEFAULT_API_ENDPOINT = "https://api.zenhub.io"

    def __init__(self, api_token, api_endpoint=None):
        self.api_token = api_token
        self.api_endpoint = api_endpoint or ZenHub.DEFAULT_API_ENDPOINT

    def repository(self, repo_id):
        return ZenHub.Repo(repo_id, self)

    def release(self, release_id):
        return ZenHub.Release(release_id=release_id, zenhub=self)

    def get(self, path):
        url = f"{self.api_endpoint}{path}"
        response = requests.get(url, headers={"X-Authentication-Token": self.api_token})
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            raise RuntimeError(f"Unexpected response: {response}")

    def post(self, path, body):
        url = f"{self.api_endpoint}{path}"
        response = requests.post(url, json=body, headers={"X-Authentication-Token": self.api_token})
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            raise RuntimeError(f"Unexpected response: {response}")

    def patch(self, path, body):
        url = f"{self.api_endpoint}{path}"
        response = requests.patch(url, json=body, headers={"X-Authentication-Token": self.api_token})
        if response.status_code == requests.codes.ok:
            return response.json()
        else:
            raise RuntimeError(f"Unexpected response: {response}")

    class Repo:
        def __init__(self, repo_id, zenhub):
            self.id = repo_id
            self.zenhub = zenhub

        def __str__(self):
            return f"{self.__class__.__name__}[{self.id}]"

        def issue(self, issue_id):
            data = self.zenhub.get(f"/p1/repositories/{self.id}/issues/{issue_id}")
            return ZenHub.Issue(data, id=issue_id, repo=self)

        def epics(self):
            epics_data = self.zenhub.get(f"/p1/repositories/{self.id}/epics")
            return [
                ZenHub.Epic(epic_data, id=epic_data['issue_number'], repo=self)
                for epic_data in epics_data['epic_issues']
            ]

        def epic(self, epic_id):
            data = self.zenhub.get(f"/p1/repositories/{self.id}/epics/{epic_id}")
            return ZenHub.Epic(data, id=epic_id, repo=self)

        def board(self):
            data = self.zenhub.get(f"/p1/repositories/{self.id}/board")
            return ZenHub.Board(data, repo=self)

        def releases(self):
            data = self.zenhub.get(f"/p1/repositories/{self.id}/reports/releases")
            return [ZenHub.Release(release_data=release_data, zenhub=self.zenhub) for release_data in data]

    class Release:
        def __init__(self, zenhub, release_id=None, release_data=None):
            if not release_id and not release_data:
                raise RuntimeError("You must supply release_id or release_data")
            self.zenhub = zenhub
            if release_id:
                self.data = self.zenhub.get(f"/p1/reports/release/{release_id}")
            else:
                self.data = release_data

        def __str__(self):
            return f"{self.__class__.__name__} \"{self.title}\""

        def __repr__(self):
            return f"{self.__class__.__name__}[{self.id}]"

        @property
        def id(self):
            return self.data['release_id']

        @property
        def title(self):
            return self.data['title']

        def add_issues(self, issues):
            path = f"/p1/reports/release/{self.id}/issues"
            issue_data = [{'repo_id': issue.repo.id, 'issue_number': issue.number} for issue in issues]
            body = {'add_issues': issue_data, 'remove_issues': []}
            return self.zenhub.patch(path, body=body)

    class Issue:
        def __init__(self, issue_data, id, repo):
            self.repo = repo
            self.data = issue_data
            self.id = id

        def __str__(self):
            return f"{self.__class__.__name__}[{self.repo.id}/{self.id}]: {self.data}"

        @property
        def repo_id(self):
            return self.repo.id

        @property
        def number(self):
            return self.id

    class Epic:
        def __init__(self, issue_data, id, repo):
            self.repo = repo
            self.data = issue_data
            self.id = id

        def __str__(self):
            return f"{self.__class__.__name__}[{self.repo.id}/{self.id}]"

        @property
        def pipeline(self):
            try:
                return self.data['pipeline']['name']
            except KeyError:
                return None

        def raw_issues(self):
            return self.data['issues']

        def issues(self):
            return [
                self.repo.zenhub.repository(issue_data['repo_id']).issue(issue_data['issue_number'])
                for issue_data in self.data['issues']
            ]

        def add_issues(self, issues):
            path = f'/p1/repositories/{self.repo.id}/epics/{self.id}/update_issues'
            body = {
                'add_issues': [{'repo_id': issue.repo.id, 'issue_number': issue.number} for issue in issues],
            }
            self.repo.zenhub.post(path, body)

    class Board:
        def __init__(self, data, repo):
            self.repo = repo
            self.data = data

        def __str__(self):
            return f"{self.__class__.__name__}[{self.repo.id}]\n" + json.dumps(self.data, indent=4)

        def pipelines(self):
            return self.data['pipelines']

        def pipeline(self, name):
            return self.pipelines().get(name)
