import git
import questionary

def push_to_remote(repo_path='.'):
    """Push changes to a remote Git repository with user confirmation."""
    repo = git.Repo(repo_path)
    
    # Get the current branch name
    current_branch = repo.active_branch.name
    
    # Ask if the user wants to push the current branch
    push_current = questionary.confirm(f"Do you want to push code from the current branch ({current_branch})?").ask()
    
    if push_current:
        branch_name = current_branch
    else:
        # Ask if the user wants to push another branch
        push_another = questionary.confirm("Do you want to push code from another branch?").ask()
        
        if push_another:
            # Get all local branches
            branches = [str(branch) for branch in repo.branches]
            branch_name = questionary.select("Which branch do you want to push?", choices=branches).ask()
        else:
            print("Push operation cancelled.")
            return
    
    # Confirm with the user
    confirm_push = questionary.confirm(f"Are you sure you want to push code from {branch_name}?").ask()
    
    if confirm_push:
        try:
            # Push changes
            repo.git.push('origin', branch_name)
            print(f"Successfully pushed to origin/{branch_name}")
        except git.GitCommandError as e:
            print(f"Failed to push to origin/{branch_name}. Error: {e}")
    else:
        print("Push operation cancelled.")