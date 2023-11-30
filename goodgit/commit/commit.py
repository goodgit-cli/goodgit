import re
import git
import json
import requests
import subprocess
import questionary
from halo import Halo
from rich import print

from .add import git_unadd
from goodgit.utils import is_git_repo

def get_git_diff():
    """
    Gets the git diff for the HEAD.
    
    Returns:
        str: The git diff output.
    """
    result = subprocess.run(["git", "diff", "--staged"], capture_output=True, text=True)
    return result.stdout

def highlight_keywords(text):
    """
    Highlights keywords enclosed in backticks within the text.
    
    Parameters:
        text (str): The text to highlight.
        
    Returns:
        str: The text with highlighted keywords.
    """
    return re.sub(r"`(.*?)`", "[bold white]\\1[/bold white]", text)

def commit():
    """
    Main function to handle the git commit operation.
    """
    repo = git.Repo(".")
    if not repo.is_dirty():
        print("[green]All clean, Nothing to commit[/green]")
        return False
    
    spinner = Halo(text='Baking your commit', spinner='moon')
    
    spinner.start()
    
    # Get the git diff
    git_diff = get_git_diff()
    
    # Prepare the payload for the API call
    payload = json.dumps({
        "git_diff": git_diff,
    })

    headersList = {
        "Accept": "*/*",
        "User-Agent": "GoodGit",
        "Content-Type": "application/json",
    }

    reqUrl = "https://api.goodgit.io/api/commit/"
    response = requests.request("POST", reqUrl, data=payload,  headers=headersList)
    
    spinner.stop()

    # Handle the API response
    if response.status_code == 200:
        commit_json = response.json()
        print(f"[bold orange1]{highlight_keywords(commit_json['subject'])}[/bold orange1]")
        print(f"[white]{highlight_keywords(commit_json['description'])}[/white]")

        commit_choice = questionary.confirm("Do you want to commit with this message?").ask()
        if commit_choice:
            result = subprocess.run(["git", "commit", "-m", commit_json['subject'], "-m", commit_json['description']], capture_output=True, text=True)
            if result.returncode != 0:
                git_unadd()
                print(f"[red]Commit failed: {result.stderr}[/red]")
                return False
            else:
                print("[bold green]Commit successful![/bold green]")
                return True
                
        else:
            git_unadd()
            print("[yellow]Commit cancelled. All changes have been unstaged.[/yellow]")
            return False
    else:
        print("[red]API call failed. Exiting.[/red]")
        return False
