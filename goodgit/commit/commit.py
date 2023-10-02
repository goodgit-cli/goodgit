import subprocess
import requests
import json
import questionary
from rich import print
from goodgit.utils import is_git_repo
from .add import git_unadd
import re

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
    return re.sub(r"`(.*?)`", "[bold yellow]\\1[/bold yellow]", text)

def commit():
    """
    Main function to handle the git commit operation.
    """
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

    reqUrl = "https://orca-app-qmx5i.ondigitalocean.app/api/commit/"
    response = requests.request("POST", reqUrl, data=payload,  headers=headersList)

    # Handle the API response
    if response.status_code == 200:
        commit_json = response.json()
        print(f"[bold yellow]{highlight_keywords(commit_json['subject'])}[/bold yellow]")
        print(f"[yellow]{highlight_keywords(commit_json['description'])}[/yellow]")

        commit_choice = questionary.confirm("Do you want to commit with this message?").ask()
        if commit_choice:
            result = subprocess.run(["git", "commit", "-m", commit_json['subject'], "-m", commit_json['description']], capture_output=True, text=True)
            if result.returncode != 0:
                git_unadd()
                print(f"[red]Commit failed: {result.stderr}[/red]")
            else:
                print("[green]Commit successful![/green]")
                
        else:
            git_unadd()
            print("[yellow]Commit cancelled. All changes have been unstaged.[/yellow]")
    else:
        print("[red]API call failed. Exiting.[/red]")
