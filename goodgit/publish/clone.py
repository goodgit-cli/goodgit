import json
import re
import subprocess
from questionary import prompt
import os

def clone_repo(repo_link=None):
    config_path = os.path.expanduser("~/.ssh/goodgit/config.json")

    # Load config file
    with open(config_path, "r") as f:
        config = json.load(f)

    # If repo_link is not provided, ask user for it
    if repo_link is None:
        questions = [
            {
                'type': 'text',
                'name': 'repo_link',
                'message': 'Enter the SSH or HTTPS link of the Git repo you want to clone:',
            }
        ]
        answers = prompt(questions)
        repo_link = answers['repo_link']

    # Validate and possibly convert link
    if re.match(r"git@github\.com:[\w-]+/[\w-]+\.git", repo_link):
        print(f"SSH link provided: {repo_link}")
    elif re.match(r"https://github\.com/[\w-]+/[\w-]+\.git", repo_link):
        print(f"HTTPS link provided, converting to SSH: {repo_link}")
        user_repo = repo_link.replace("https://github.com/", "")
        repo_link = f"git@github.com:{user_repo}"
        print(repo_link)
    else:
        print("Invalid link provided.")
        return  # Exit function instead of entire script

    # Check number of accounts in config
    if len(config["accounts"]) > 1:
        email_options = [acc["email"] for acc in config["accounts"]]
        questions = [
            {
                'type': 'select',
                'name': 'email',
                'message': 'Select the account to clone from:',
                'choices': email_options,
            }
        ]
        answers = prompt(questions)
        selected_email = answers['email']
        selected_host = next(acc["host"] for acc in config["accounts"] if acc["email"] == selected_email)
        
        # Replace github.com with selected host
        new_repo_link = repo_link.replace("github.com", selected_host)
        print(f"Cloning from {new_repo_link}")
        subprocess.run(["git", "clone", new_repo_link])
    else:
        print(f"Cloning from {repo_link}")
        subprocess.run(["git", "clone", repo_link])

