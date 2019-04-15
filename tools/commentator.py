from . import output


class Commentator:

    @classmethod
    def configure(cls, subparsers):
        comment_parser = subparsers.add_parser('comment', description="comment on all issues attached to epic")
        comment_parser.set_defaults(command='comment')
        comment_parser.add_argument('epic_id', type=str)
        comment_parser.add_argument('comment', type=str, metavar="\"comment\"")

    def __init__(self, zenhub, github):
        self.zenhub = zenhub
        self.github = github

    def run(self, args):
        zh_repo = self.zenhub.repository(args.repo_id)
        epic = zh_repo.epic(args.epic_id)
        for issue in epic.raw_issues():
            gh_repo = self.github.get_repo(issue['repo_id'])
            gh_issue = gh_repo.get_issue(issue['issue_number'])
            output(f"{gh_repo.full_name} {gh_issue.number} \"{gh_issue.title}\"...")
            if gh_issue.state == "open":
                gh_issue.create_comment(args.comment)
                output(" commenting.\n")
            else:
                output(f" is {gh_issue.state}, skipping.\n")
