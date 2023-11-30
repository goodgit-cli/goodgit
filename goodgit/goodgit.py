"""
GoodGit CLI

Usage:
    gg <command> [<args>...]
    gg -h | --help

Options:
    -h --help   Show this screen.

Commands:
    init        Initiate Git Repo with main branch
    add         Add files, AI commit, and push
    branch      List, switch, create new branches
    commit      Add, AI commit, push
    uncommit    Undo the last commit.
    merge       Merge branches.
    pull        Pull from the current branch. Or specify the branch
    publish     Publish the repository to GitHub
    search      Search the git repository.
    setup       Setup SSH in 10secs. Multiple accounts supported
    clone       Clone a repo from an account you want
    web         Open repository in web browser.
    timetravel  Time travel in your commits
    tt          Time travel in your commits

    timetravel apply    Make a time travelled commit your present commit
    tt apply            Make a time travelled commit your present commit
    
Git:
    All git commands work with "gg <command>" for when you really need the underlying powers of git.
"""

import subprocess
import platform

def check_requirements():
    os_type = platform.system()
    
    # Check for Git installation
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print("Git is not installed. Please install Git to use GoodGit.")
        return False

    if os_type == "Windows":
        pass
    else:
        pass

    return True


if check_requirements():
    pass
else:
    print("Requirements not met. Exiting.")
    exit(1)

import sys
import questionary
from rich import print
from docopt import docopt

from goodgit.web import gg_web
from goodgit.ssh import add_ssh_account
from .analytics import unblocking_logalytics
from goodgit.search import git_grep_interactive
from goodgit.merge import merge_branches, pull_changes
from goodgit.publish import publish as ggpublish, clone_repo
from goodgit.branch import list_branches, new_branch, switch_branch
from goodgit.timetravel import timetravel as ggtimetravel, apply_timetravel
from goodgit.commit import add as ggadd, commit as ggcommit, push_to_remote, uncommit as gguncommit, initialize_git_repo

class GoodGit:
    def branch(self):
        list_branches()
        
        choices = ['Nope, that\'s it', 'Create a new branch', 'Switch branch']

        selection = questionary.select(
            "Anything else?",
            choices=choices
        ).ask()

        if selection == choices[1]:
            new_branch()

        elif selection == choices[2]:
            switch_branch()
        
        else:
            return
        
    def init(self):
        initialize_git_repo()
        
    def clone(self, repo_link=None):
        clone_repo(repo_link)
        
    def commitpush(self):
        if ggcommit():
            remote = push_to_remote()
            # if not remote, then ask if user wants to publish
            if remote == "Not Remote":
                to_publish = questionary.confirm("Do you want to add this repository to your github?").ask()
                if to_publish:
                    # publish to github
                    ggpublish()
    
    def add(self, *args):
        if len(args) == 0:
            ggadd()
        elif args[0] in ['*', '.']:
            # The wild route: add all files
            ggadd("*")
        else:
            # The tailored route: add specified files
            ggadd(list(args))
            
        self.commitpush()
        
    def commit(self):
        ggadd()
        # check if commit success
        self.commitpush()

    def uncommit(self):
        gguncommit()

    def merge(self):
        merge_branches()
        
    def pull(self, remote=None, branch=None):
        pull_changes(remote, branch)

    def publish(self):
        ggpublish()

    def search(self):
        git_grep_interactive()

    def setup(self):
        add_ssh_account()
        
    def web(self):
        gg_web()
        
    def handle_timetravel(self, apply):
        if apply:
            apply_timetravel()
        else:
            ggtimetravel()

    def timetravel(self, apply=False):
        self.handle_timetravel(apply)
    
    def tt(self, apply=False):
        self.handle_timetravel(apply)
            
    # TODO: Scream command

    def git(self, *args):
        cmd_list = ['git'] + list(args)
        result = subprocess.run(cmd_list, text=True, capture_output=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)


def main():
    args = docopt(__doc__, options_first=True)
    
    unblocking_logalytics(args)
    
    gg = GoodGit()
    command = args['<command>']
    cmd_args = args['<args>']
    
    if hasattr(gg, command):
        func = getattr(gg, command)
        func(*cmd_args)
    else:
        gg.git(command, *cmd_args)
