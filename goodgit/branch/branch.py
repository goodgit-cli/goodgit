import git
import questionary
from rich import print

def get_current_branch(repo):
    """Get the name of the current Git branch."""
    return repo.active_branch.name

def get_uncommitted_changes(repo):
    """Check for uncommitted changes in the repository."""
    return repo.is_dirty()

def temporary_commit(repo):
    """Create a temporary commit to save changes."""
    repo.git.add(A=True)
    repo.git.commit(m="TEMP_COMMIT")

def undo_temporary_commit(repo):
    """Undo the last temporary commit."""
    last_commit_message = repo.head.commit.message
    if last_commit_message.strip() == "TEMP_COMMIT":
        repo.git.reset("HEAD~")

def switch_branch(repo=git.Repo('.'), branch_name=""):
    """Switch to a different Git branch."""
    if get_uncommitted_changes(repo):
        temporary_commit(repo)
    
    branches = [str(branch) for branch in repo.branches]
    if not branch_name:
        branch_name = questionary.select("Select a branch to switch to:", choices=branches).ask()
    
    if branch_name not in branches:
        create_new = questionary.confirm(f"Branch {branch_name} doesn't exist. Do you want to create it?").ask()
        if create_new:
            new_branch(repo, branch_name)
            return
    
    repo.git.checkout(branch_name)
    undo_temporary_commit(repo)
    
def list_branches(repo=git.Repo('.')):
    """List all branches in the repository."""
    current_branch = get_current_branch(repo)
    branches = [str(branch) for branch in repo.branches]
    print("[blue]Available branches:[/blue]")
    for branch in branches:
        if branch == current_branch:
            print(f"- [white bold]{branch}[/white bold] (current)")
        else:
            print(f"- [white]{branch}[/white]")

def new_branch(repo=git.Repo('.'), branch_name=""):
    """Create a new Git branch."""
    if get_uncommitted_changes(repo):
        temporary_commit(repo)
    
    if not branch_name:
        branch_name = questionary.text("Enter the new branch name: ").ask()
    
    branches = [str(branch) for branch in repo.branches]
    if branch_name in branches:
        switch = questionary.confirm(f"Branch {branch_name} already exists. Do you want to switch to it?").ask()
        if switch:
            switch_branch(repo, branch_name)
            return
    
    repo.git.checkout(b=branch_name)
    undo_temporary_commit(repo)