import subprocess
import re
import questionary
from rich import print

def run_command(command, input=None, capture_output=True, text=True, check=True):
    try:
        result = subprocess.run(command, input=input, capture_output=capture_output, text=text, check=check)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[red]Command failed: {e}[/red]")
        exit(1)

def temp_commit():
    uncommitted_changes = run_command(["git", "status", "--porcelain"])
    if uncommitted_changes:
        run_command(["git", "add", "-A"])
        run_command(["git", "commit", "-m", "TEMP_COMMIT"])

def undo_temp_commit():
    last_commit_message = run_command(["git", "log", "-1", "--pretty=%B"]).strip()
    if last_commit_message == "TEMP_COMMIT":
        run_command(["git", "reset", "HEAD~"])

def validate_branch_name(branch_name):
    # Assuming a simple naming convention for demonstration
    if re.match(r'^[a-zA-Z0-9_-]+$', branch_name):
        return True
    print("[red]Invalid branch name![/red]")
    return False

def list_branches():
    branches = run_command(["git", "branch", "--list"]).split("\n")
    for branch in branches:
        print(branch)

def switch_branch():
    temp_commit()
    branches = run_command(["git", "branch", "--list"]).split("\n")
    branches = [branch.strip() for branch in branches if branch]  # cleaning up any whitespace and empty strings
    branches.append("Create a new branch")
    
    branch_selection = questionary.select(
        "Choose a branch to switch to or create a new one:",
        choices=branches
    ).ask()
    
    if branch_selection == "Create a new branch":
        new_branch()
    else:
        run_command(["git", "checkout", branch_selection])
        undo_temp_commit()


def new_branch(branch_name=""):
    temp_commit()
    if not branch_name:
        branch_name = questionary.text("Enter the new branch name: ", validate=validate_branch_name).ask()
    if branch_name in run_command(["git", "branch", "--list"]):
        switch = questionary.confirm(f"Branch {branch_name} already exists. Do you want to switch to it?").ask()
        if switch:
            switch_branch(branch_name)
            return
    run_command(["git", "checkout", "-b", branch_name])
    undo_temp_commit()
