from . import output


class Commentator:

    @classmethod
    def configure(cls, subparsers):
        comment_parser = subparsers.add_parser('comment', description="comment on all issues attached to epic")
        comment_parser.set_defaults(command='comment')
        comment_parser.add_argument('epic_id', type=str)
        comment_parser.add_argument('comment', type=str, metavar="\"comment\"")

    def __init__(self, combo):
        self.combo = combo

    def run(self, args):
        repo = self.combo.repo(args.repo_name)
        epic = repo.epic(args.epic_id)
        print(epic)
        for issue in epic.issues():
            output(f"{issue}...")
            if issue.status == "open":
                issue.gh_issue.create_comment(args.comment)
                output(" commenting.\n")
            else:
                output(f" is {issue.status}, skipping.\n")
