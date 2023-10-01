import git
import webbrowser
import re

def gg_web():
    try:
        # Initialize a git Repo object
        repo = git.Repo(search_parent_directories=True)
        
        # Check if there are any remotes
        if not repo.remotes:
            print("This Git repository is not connected to any remote repository.")
            return
        
        # Fetch the remote URL
        try:
            remote_url = repo.remotes.origin.url
        except AttributeError:
            print("This Git repository is not connected to any remote repository.")
            return
        
        # Convert SSH URL to HTTPS URL if needed
        if remote_url.startswith("git@"):
            remote_url = "https://" + remote_url[4:].replace(":", "/").replace(".git", "")
            remote_url = re.sub(r'github-[^/]+', 'github.com', remote_url)
        
        # Open the URL in the default web browser and detach the process
        webbrowser.open(remote_url)
    except git.InvalidGitRepositoryError:
        print("There's no active Git repository in this directory.")
    except Exception as e:
        print(f"An error occurred: {e}")