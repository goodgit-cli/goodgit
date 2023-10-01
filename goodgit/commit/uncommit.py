import git
from .add import git_unadd

def uncommit():
    try:
        # Initialize a git object for the current directory
        repo = git.Repo(".")
        
        # Check the number of commits
        num_commits = len(list(repo.iter_commits()))
        
        if num_commits > 1:
            # Get the last commit message
            last_commit_message = repo.head.commit.message
            
            # Perform the soft reset
            repo.git.reset("--soft", "HEAD~1")
            git_unadd()
            
            print(f"Successfully undone '{last_commit_message}'.")
        elif num_commits == 1:
            # Get the last commit message
            last_commit_message = repo.head.commit.message
            
            # Delete the last commit
            repo.git.update_ref("-d", "HEAD")
            git_unadd()
            
            print(f"Successfully deleted the only commit '{last_commit_message}'.")
        else:
            print("No commits to undo.")
            
    except git.InvalidGitRepositoryError:
        print("You're not in a Git repository.")
    except git.GitCommandError as e:
        print(f"Failed to undo the last commit. Error: {e}")

if __name__ == "__main__":
    uncommit()

