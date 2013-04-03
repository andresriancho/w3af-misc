import argparse
import sys
import functools 

from multiprocessing.pool import ThreadPool

from github import Github, GithubException


def parse():
    parser = argparse.ArgumentParser(prog='fork_info',
                                     description='Get information about a Github project forks')
    parser.add_argument('--project', type=str, default='andresriancho/w3af', help='<username>/<project name>')
    parser.add_argument('--username', type=str, default='andresriancho', help='Github username to connect via API')
    parser.add_argument('--password', type=str, default='', help='Github password to connect via API', required=True)

    args = parser.parse_args()

    return args

def extract_fork_info(project_name, gh):
    target_repo = gh.get_user().get_repo('w3af')

    existing_target_branches = [b.name for b in target_repo.get_branches()]

    fork_list = target_repo.get_forks()

    analyze_branches(existing_target_branches, fork_list)
    analyze_commits(project_name, target_repo, existing_target_branches, fork_list)

def analyze_branches(existing_target_branches, fork_list):
    print 'Analyzing branches'
    for fork_repo in fork_list:
        print '    Analyzing', fork_repo.full_name

        fork_branches = [b.name for b in fork_repo.get_branches()]
        for fork_branch in fork_branches:
            if fork_branch not in existing_target_branches:
                msg = '    Branch %s does NOT exist in the root repository but exists in %s'
                print msg % (fork_branch, fork_repo.full_name)


def analyze_commits(project_name, target_repo, existing_target_branches, fork_list):
    print 'Analyzing commits'

    pool = ThreadPool(processes=10)

    existing_target_commits = []

    for fork_repo in fork_list:
        for target_branch in existing_target_branches:

            print '    Analyzing %s (branch: %s) ' % (fork_repo.full_name, target_branch),
            fork_repo_commits = fork_repo.get_commits(sha=target_branch)

            max_commits_to_analyze = 30
            analyzed_commits = 0

            fork_commits_to_analyze = []

            for fork_comm in fork_repo_commits:
                if analyzed_commits == max_commits_to_analyze:
                    break

                fork_commits_to_analyze.append(fork_comm)

                analyzed_commits += 1

            partial_c_in_root = functools.partial(commit_is_in_root,
                                                  existing_target_commits,
                                                  target_repo, fork_repo)

            pool.map(partial_c_in_root, fork_commits_to_analyze)
            print

def commit_is_in_root(existing_target_commits, target_repo, fork_repo, fork_comm):
    if fork_comm.sha in existing_target_commits:
        # It's a known commit, nothing to do here
        return

    try:
        target_commit = target_repo.get_commit(fork_comm.sha)
    except GithubException:
        print '        Found new commit %s in %s' % (fork_comm.sha, fork_repo.full_name)
    else:
        # Commit exists in w3af
        existing_target_commits.append(target_commit.sha)

        #print '        Added %s to known %s commits.' % (target_commit.sha, project_name)
        sys.stdout.write('.')
        sys.stdout.flush()

        return

if __name__ == '__main__':
    args = parse()

    github = Github(args.username, args.password)

    extract_fork_info(args.project, github)

    sys.exit(0)
