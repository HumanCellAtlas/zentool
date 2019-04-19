from . import output


class ReleaseAssigner:
    """
    export GITHUB_API_TOKEN=x ZENHUB_API_TOKEN=y
    zentool -r HumanCellAtlas/dcp release <epic_id> "General Availability"
    """

    @classmethod
    def configure(cls, subparsers):
        assigner_parser = subparsers.add_parser('release', description="Assign all tickets attached to epic to release")
        assigner_parser.set_defaults(command='release')
        assigner_parser.add_argument('epic_id', type=str)
        assigner_parser.add_argument('release_name', type=str,
                                     help="name of release to assign epic issues to (use quotes if spaces)")

    def __init__(self, combo):
        self.combo = combo

    def run(self, args):
        release_name = args.release_name
        repo = self.combo.repo(args.repo_name)
        print(repo)
        epic = repo.epic(args.epic_id)
        print(epic)
        releases = repo.zen.releases()
        release_names = [rel.title for rel in releases]
        if release_name not in release_names:
            print(f"Unknown release \"{release_name}\". Known releases are {release_names}")
            exit(1)
        release = [rel for rel in releases if rel.title == release_name][0]
        print(release)
        for issue in epic.issues():
            try:
                output(f"Adding {issue} to {release}...")
                resp = release.add_issues([issue])
                if resp == {'added': [], 'removed': []}:
                    print("NO CHANGE")
                elif len(resp['added']) > 0:
                    print("SUCCESS")
            except Exception as e:
                print(f"FAILED: {e}")

