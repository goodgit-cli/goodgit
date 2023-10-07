import requests
import json
import time
import os
import subprocess
from urllib.parse import parse_qs
from questionary import text, select, confirm
from rich import print
from rich.console import Console

from goodgit.ssh import add_ssh_account
from goodgit.utils import check_git_remote
from goodgit.commit import push_to_remote, add, commit
from goodgit.github import fetch_github_username, retrieve_github_access_token, create_github_repo, get_new_access_token

console = Console()

def check_ssh_connection():
    result = subprocess.run(["ssh", "-T", "git@github.com"], capture_output=True, text=True)
    if "You've successfully authenticated" not in result.stderr:
        return False
    return True

def load_host_mapping():
    try:
        with open(os.path.expanduser("~/.ssh/goodgit/config.json"), "r") as f:
            data = json.load(f)
            return {account['email']: account['host'] for account in data.get("accounts", [])}
    except FileNotFoundError:
        return {}

def load_accounts():
    try:
        with open(os.path.expanduser("~/.ssh/goodgit/config.json"), "r") as f:
            data = json.load(f)
            return data.get("accounts", [])
    except FileNotFoundError:
        return []

def handle_existing_git_remote():
    is_git_initialized, remote_link = check_git_remote()
    if is_git_initialized:
        console.print(f"A git remote link is already set up: [bold orange1]{remote_link}[/bold orange1]")
        user_choice = select(
            "Would you like to push the code to this remote?",
            choices=["Yes", "No"]
        ).ask()
        if user_choice == 'Yes':
            push_to_remote()
        return True
    return False

def select_email_from_accounts(accounts):
    if len(accounts) == 0:
        print("[red]No accounts found[/red]")
        email = add_ssh_account()
        if email:
            return email
        else:
            print("[bold orange1]We weren't prepared for you to say no :([/bold orange1]")
            exit(1)
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
    specific_host = host_mapping.get(selected_email, "github.com")
    console.print(f"Pushing to repo: [bold green]{repo_name}[/bold green], Username: [bold green]{username}[/bold green], Host: [bold green]{specific_host}[/bold green]")
    
    subprocess.run("git init", shell=True)
    add()
    commit()
    
    remaining_commands = [
        "git branch -M main",
        f"git remote add origin git@{specific_host}:{username}/{repo_name}.git",
        "git push -u origin main"
    ]
    
    for cmd in remaining_commands:
        subprocess.run(cmd, shell=True)

def create_and_push_new_repo(selected_email, host_mapping):
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
    repo_name = text("Enter the name for your new GitHub repository:").ask()
    is_private = select(
        "Should the repository be private or public?",
        choices=["Private", "Public"]
    ).ask() == "Private"
    return repo_name, is_private

def publish():
    config_path = os.path.expanduser("~/.ssh/goodgit/config.json")
    
    if not os.path.exists(config_path):
        console.print("[red]Config file does not exist.[/red]")
        
        if check_ssh_connection():
            console.print("[green]SSH connection to GitHub is already set up.[/green]")
        else:
            console.print("[red]SSH connection not established. Running add_ssh_account...[/red]")
            email = add_ssh_account()
            if email:
                console.print(f"[green]Successfully added SSH account for {email}[/green]")
            else:
                console.print("[red]Failed to add SSH account. Exiting.[/red]")
                exit(1)
                
    host_mapping = load_host_mapping()
    accounts = load_accounts()
    
    if not handle_existing_git_remote():
        selected_email = select_email_from_accounts(accounts)
        if selected_email:
            create_and_push_new_repo(selected_email, host_mapping)
