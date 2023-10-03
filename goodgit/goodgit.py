"""
GoodGit CLI

Usage:
    gg <command> [<args>...]
    gg -h | --help

Options:
    -h --help   Show this screen.

Commands:
    branch      Handle branches.
    commit      Handle commits.
    uncommit    Undo the last commit.
    merge       Merge branches.
    publish     Publish the repository.
    search      Search the git repository.
    setup       Setup SSH.
    web         Open repository in web browser.
    timetravel  Time travel functionality.
"""

import sys
import subprocess
import questionary
from docopt import docopt

from goodgit.web import gg_web
from goodgit.ssh import add_ssh_account
from goodgit.merge import merge_branches
from goodgit.search import git_grep_interactive
from goodgit.publish import publish as ggpublish
from goodgit.branch import list_branches, new_branch, switch_branch
from goodgit.timetravel import timetravel as ggtimetravel, apply_timetravel
from goodgit.commit import add as ggadd, commit as ggcommit, push_to_remote, uncommit as gguncommit

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
        if args[0] in ['*', '.']:
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

    def publish(self):
        ggpublish()

    def search(self):
        git_grep_interactive()

    def setup(self):
        add_ssh_account()
        
    def web(self):
        gg_web()

    def timetravel(self, apply=False):
        if apply:
            apply_timetravel()
        else:
            ggtimetravel()

    def git(self, *args):
        cmd_list = ['git'] + list(args)
        result = subprocess.run(cmd_list, text=True, capture_output=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)


def main():
    args = docopt(__doc__, options_first=True)
    gg = GoodGit()
    command = args['<command>']
    cmd_args = args['<args>']
    
    if hasattr(gg, command):
        func = getattr(gg, command)
        func(*cmd_args)
    else:
        gg.git(command, *cmd_args)
