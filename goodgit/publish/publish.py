import requests
import json
import time
import os
import subprocess
from urllib.parse import parse_qs
from questionary import text, select, confirm
from rich import print as rprint
from rich.console import Console

from goodgit.utils import check_git_remote
from goodgit.commit import push_to_remote, add, commit
from goodgit.github import fetch_github_username, retrieve_github_access_token, create_github_repo, get_new_access_token

console = Console()

def load_host_mapping():
    """Load host mapping from the configuration file."""
    try:
        with open(os.path.expanduser("~/.ssh/goodgit/config.json"), "r") as f:
            data = json.load(f)
            return {account['email']: account['host'] for account in data.get("accounts", [])}
    except FileNotFoundError:
        return {}

def load_accounts():
    """Load accounts from the configuration file."""
    try:
        with open(os.path.expanduser("~/.ssh/goodgit/config.json"), "r") as f:
            data = json.load(f)
            return data.get("accounts", [])
    except FileNotFoundError:
        return []

def handle_existing_git_remote():
    """Handle the case where a git remote already exists."""
    is_git_initialized, remote_link = check_git_remote()
    if is_git_initialized:
        console.print(f"A git remote link is already set up: [bold yellow]{remote_link}[/bold yellow]")
        user_choice = select(
            "Would you like to push the code to this remote?",
            choices=["Yes", "No"]
        ).ask()
        if user_choice == 'Yes':
            push_to_remote()
        return True
    return False

def select_email_from_accounts(accounts):
    """Select an email account to use for GitHub operations."""
    if len(accounts) == 0:
        # Check if 'github.com' exists in known hosts
        known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
        if os.path.exists(known_hosts_path):
            with open(known_hosts_path, 'r') as f:
                if 'github.com' in f.read():
                    selected_email = text("Please enter your GitHub email address:").ask()
                    if selected_email:
                        return selected_email
                    
        console.print("[bold red]No accounts found and 'github.com' not in known hosts. Exiting.[/bold red]")
        # TODO: create account if it doesn't exist
        return None
    elif len(accounts) == 1:
        selected_email = accounts[0]['email']
        console.print(f"Using the only available account: [bold green]{selected_email}[/bold green]")
    else:
        selected_email = select(
            "Select the account you want to use:",
            choices=[account['email'] for account in accounts]
        ).ask()
    return selected_email


def push_to_repo(repo_name, username, selected_email, host_mapping):
    """Push the local repository to the remote GitHub repository."""
    specific_host = host_mapping.get(selected_email, "github.com")
    console.print(f"Pushing to repo: [bold green]{repo_name}[/bold green], Username: [bold green]{username}[/bold green], Host: [bold green]{specific_host}[/bold green]")
    
    subprocess.run("git init", shell=True)
    add()  # Custom 'git add' Python function
    commit()  # Custom 'git commit' Python function
    
    remaining_commands = [
        "git branch -M main",
        f"git remote add origin git@{specific_host}:{username}/{repo_name}.git",
        "git push -u origin main"
    ]
    for cmd in remaining_commands:
        subprocess.run(cmd, shell=True)

def create_and_push_new_repo(selected_email, host_mapping):
    """Create a new GitHub repository and push the local code to it."""
    access_token = retrieve_github_access_token(selected_email)
    if not access_token:
        access_token = get_new_access_token(selected_email)
        if not access_token:
            console.print("[bold red]Failed to get access token within the allowed time. Exiting.[/bold red]")
            return

    username = fetch_github_username(access_token)
    if not username:
        console.print("[bold red]Failed to fetch GitHub username. Exiting.[/bold red]")
        return

    while True:
        repo_name, is_private = get_repo_details()
        created_repo_name = create_github_repo(access_token, repo_name, is_private)
        if created_repo_name:
            console.print(f"Successfully created repository: [bold green]{created_repo_name}[/bold green]")
            time.sleep(2)
            push_to_repo(created_repo_name, username, selected_email, host_mapping)
            break
        else:
            console.print("[bold red]Name already exists. Let's try again with a different name.[/bold red]")

def get_repo_details():
    """Get the name and privacy setting for the new GitHub repository."""
    repo_name = text("Enter the name for your new GitHub repository:").ask()
    is_private = select(
        "Should the repository be private or public?",
        choices=["Private", "Public"]
    ).ask() == "Private"
    return repo_name, is_private

def publish():
    """Main function to execute the script."""
    host_mapping = load_host_mapping()
    
    accounts = load_accounts()
    if not handle_existing_git_remote():
        selected_email = select_email_from_accounts(accounts)
        if selected_email:
            create_and_push_new_repo(selected_email, host_mapping)
