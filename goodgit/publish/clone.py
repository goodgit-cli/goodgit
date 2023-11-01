import json
import re
import subprocess
from questionary import prompt
import os

from goodgit.github import retrieve_github_access_token, get_github_username

def clone_repo(repo_link=None):
    config_path = os.path.expanduser("~/.ssh/goodgit/config.json")
    
    # Check SSH connection first
    result = subprocess.run(["ssh", "-T", "git@github.com"], capture_output=True, text=True)
    
    if "You've successfully authenticated" not in result.stderr:
        print("SSH connection to GitHub failed.")
        
        # Since SSH failed, now check if config file exists
        if not os.path.exists(config_path):
            print("\033[91mConfig file does not exist.\033[0m")
            
            # Prompt to create new SSH account
            questions = [
                {
                    'type': 'confirm',
                    'name': 'create_account',
                    'message': 'Do you want to create a new SSH account?',
                    'default': False
                }
            ]
            answers = prompt(questions)
            if answers.get('create_account'):
                # Import and run the function from your SSH module
                from ..ssh.ssh import add_ssh_account
                add_ssh_account()
            return
    else:
        print("SSH connection to GitHub succeeded.")
        
    # If the config file exists, read it
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception as e:
            print(f"An error occurred while reading the config file: {e}")
            return
    
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
        return
    
    # Check number of accounts in config
    if os.path.exists(config_path) and len(config["accounts"]) > 1:
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
        
        access_token = retrieve_github_access_token(selected_email)
        github_username = get_github_username(access_token)
        
        subprocess.run(["git", "config", "--local", "user.name", github_username])
        subprocess.run(["git", "config", "--local", "user.email", selected_email])
        
        selected_host = next(acc["host"] for acc in config["accounts"] if acc["email"] == selected_email)
        
        # Replace github.com with selected host
        new_repo_link = repo_link.replace("github.com", selected_host)
        print(f"Cloning from {new_repo_link}")
        subprocess.run(["git", "clone", new_repo_link])
    else:
        print(f"Cloning from {repo_link}")
        subprocess.run(["git", "clone", repo_link])

# For demonstration
if __name__ == "__main__":
    clone_repo()

