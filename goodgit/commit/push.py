import git
import questionary
from rich import print

from .add import add
from .commit import commit
from goodgit.merge import pull_changes

def push_to_remote(repo_path='.'):
    """Push changes to a remote Git repository with user confirmation."""
    repo = git.Repo(repo_path)
    
    # Check if it's a remote repository
    if not repo.remotes:
        print("[yellow]This is not a remote repository, can't push.[/yellow]")            
        return "Not Remote"
    
    status, files = pull_changes()
    if status:
        add(files)
        commit()
        
    elif not status and files:
        return False
    
    # Get the current branch name
    current_branch = repo.active_branch.name
    
    # Ask if the user wants to push the current branch
    push_current = questionary.confirm(f"Do you want to push code from the current branch ({current_branch})?").ask()
    
    if push_current:
        branch_name = current_branch
        confirm_push = True
    else:
        # Ask if the user wants to push another branch
        push_another = questionary.confirm("Do you want to push code from another branch?").ask()
        
        if push_another:
            # Get all local branches
            branches = [str(branch) for branch in repo.branches]
            branch_name = questionary.select("Which branch do you want to push?", choices=branches).ask()
            # Confirm with the user
            confirm_push = questionary.confirm(f"Are you sure you want to push code from {branch_name}?").ask()
            
        else:
            print("Push cancelled.")
            return False
    
    if confirm_push:
        try:
            # Push changes
            repo.git.push('origin', branch_name)
            print(f"[bold green]Successfully pushed to origin/{branch_name}[/bold green]")
            return True
        except git.GitCommandError as e:
            print(f"Failed to push to origin/{branch_name}. Error: {e}")
            return False
    else:
        print("Push operation cancelled.")
        return False