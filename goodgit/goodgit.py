import click
import questionary
from goodgit.branch import list_branches, new_branch, switch_branch
from goodgit.commit import add, commit as ggcommit, push_to_remote, uncommit as gguncommit
from goodgit.merge import merge_branches
from goodgit.publish import publish
from goodgit.search import git_grep_interactive
from goodgit.ssh import add_ssh_account
from goodgit.timetravel import timetravel
from goodgit.web import gg_web

@click.group()
def cli():
    """GoodGit CLI"""
    pass

@cli.command()
def branch():
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

@cli.command()
def commit():
    add()
    ggcommit()
    push_to_remote()

@cli.command()
def uncommit():
    gguncommit()

@cli.command()
def merge():
    merge_branches()

@cli.command()
def publish():
    publish()

@cli.command()
def search():
    git_grep_interactive()

@cli.command()
def setup():
    add_ssh_account()

@cli.command()
def web():
    gg_web()

@cli.command()
def timetravel():
    timetravel()