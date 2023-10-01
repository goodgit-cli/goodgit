import os
import git
import json
import platform
import subprocess
from rich import print
from questionary import prompt, Choice

# Assuming these modules exist and work as you described
from goodgit.utils import get_detailed_os_name
from goodgit.github import get_new_access_token, get_github_username, add_ssh_key_to_github


def load_accounts_from_config():
    """Load SSH accounts from the SSH config file."""
    config_path = os.path.expanduser("~/.ssh/config")
    accounts = {}
    try:
        with open(config_path, 'r') as f:
            lines = f.readlines()
        host = None
        for line in lines:
            if "Host " in line:
                host = line.split("Host ")[1].strip()
            if "User git" in line and host:
                username = host.split("github-")[-1]
                accounts[username] = host
    except FileNotFoundError:
        return {}
    return accounts


def is_default_account_set():
    """Check if a default SSH account is set."""
    config_path = os.path.expanduser("~/.ssh/config")
    try:
        with open(config_path, "r") as f:
            lines = f.readlines()
        for line in lines:
            if "Host github.com" in line.strip():
                return True
    except FileNotFoundError:
        return False
    return False


def save_accounts(accounts, default_username=None):
    """Save SSH accounts to a JSON file."""
    home = os.path.expanduser("~")
    folder_path = os.path.join(home, ".goodgit")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filepath = os.path.join(folder_path, "accounts.json")
    data = {'accounts': accounts}
    if default_username:
        data['default_username'] = default_username
    with open(filepath, 'w') as f:
        json.dump(data, f)

def update_json_config(email, host, action="add"):
    """Update the JSON configuration for SSH accounts."""
    config_path = os.path.expanduser("~/.ssh/goodgit/config.json")
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
        else:
            data = {"accounts": []}

        account_info = {"email": f"{email} (github.com)", "host": host}

        if action == "add":
            data["accounts"].append(account_info)
        elif action == "remove":
            data["accounts"] = [account for account in data["accounts"] if account != account_info]

        with open(config_path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"[red]An error occurred while updating the JSON config: {e}[/red]")


def list_accounts(accounts):
    """List available SSH accounts."""
    config_path = os.path.expanduser("~/.ssh/goodgit/config.json")
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
        accounts = data.get('accounts', [])
        print("Available accounts:")
        for idx, account in enumerate(accounts):
            print(f"{idx+1}. [white]{account['email']}[/white]")
    except FileNotFoundError:
        print("No accounts found.")

def generate_ssh_key(email, folder):
    """Generate an SSH key."""
    try:
        home = os.path.expanduser("~")
        username = email.split('@')[0]  # Extract username from email
        goodgit_folder = os.path.join(home, ".ssh", "goodgit", f'.ssh_{username}')  # Use only username for folder
        
        # Create the folder if it doesn't exist
        if not os.path.exists(goodgit_folder):
            os.makedirs(goodgit_folder)
        
        key_path = os.path.join(goodgit_folder, "id_rsa")
        subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "4096", "-C", email, "-f", key_path, "-N", ""])
        
        with open(f"{key_path}.pub", "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"An error occurred while generating the SSH key: {e}")
        return None

def read_git_config():
    """Read the git configuration."""
    try:
        repo = git.Repo(search_parent_directories=True)
        config = repo.config_reader()  # get a config reader for read-only access
        email = config.get_value("user", "email", None)
        name = config.get_value("user", "name", None)
        return email, name
    except (git.InvalidGitRepositoryError, git.GitCommandError, KeyError):
        return None, None

def update_ssh_config(username, make_default=False):
    """Update the SSH configuration."""
    config_path = os.path.expanduser("~/.ssh/config")
    config_entry_general = f"""Host github-{username}
    HostName github.com
    User git
    IdentityFile ~/.ssh/goodgit/.ssh_{username}/id_rsa
    """
    config_entry_default = f"""Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/goodgit/.ssh_{username}/id_rsa
    """
    try:
        with open(config_path, "a") as f:
            if make_default:
                f.write("\n" + config_entry_default)  # Add as default
            f.write("\n" + config_entry_general)  # Add as general
        print("SSH config updated successfully.")
    except Exception as e:
        print(f"Failed to update SSH config: {e}")


def github_device_auth(email=None):
    """Authenticate GitHub device."""
    accounts = load_accounts_from_config()
    if accounts:
        print("You have the following accounts already set up:")
        list_accounts(accounts)

    access_token = get_new_access_token(email)
    
    if access_token:
        print("Authorization successful!")
        
        config_email, config_name = read_git_config()
        if config_name:
            user_name = config_name
        else:
            user_name = get_github_username(access_token)
            if user_name:
                subprocess.run(["git", "config", "--global", "user.name", user_name])
                subprocess.run(["git", "config", "--global", "user.email", email])

        print(f"Debug: Using email {email} for SSH key generation")  # Debug statement

        os_name = get_detailed_os_name()
        computer_name = platform.node()
        title = f"GoodGit-{os_name}-{computer_name}-{user_name}"
        
        folder = f".ssh_{email.replace('@', '_').replace('.', '_')}"
        print(f"Debug: SSH key will be saved in folder {folder}")  # Debug statement

        ssh_key = generate_ssh_key(email, folder)
        
        if ssh_key:
            add_ssh_key_to_github(access_token, title, ssh_key)
        
        return email, access_token

    else:
        print("An error occurred.")
        return None, None  # Return None values if an error occurs


def add_ssh_account():
    """Add a new SSH account."""
    accounts = load_accounts_from_config()
    if accounts:
        list_accounts(accounts.keys())

    questions = [
        {
            'type': 'confirm',
            'name': 'add_new_account',
            'message': 'Do you want to add a new account?',
            'default': True
        }
    ]
    answers = prompt(questions)
    if answers['add_new_account']:
        email = prompt([
            {
                'type': 'text',
                'name': 'email',
                'message': 'Enter your email (Same as your GitHub account):'
            }
        ])['email']
        email, token = github_device_auth(email)
        
        if email and token:
            username = email.split('@')[0]
            host = accounts.get(username, f"github-{username}")  # Fetch the host for this username
            update_json_config(email, host, action="add")  # Update JSON config with the host

            config_exists = os.path.exists(os.path.expanduser("~/.ssh/config"))

            make_default_question = [
                {
                    'type': 'confirm',
                    'name': 'make_default',
                    'message': 'Do you want to make this the default GitHub SSH account?',
                    'default': False
                }
            ]

            if not config_exists or os.path.getsize(os.path.expanduser("~/.ssh/config")) == 0:
                make_default = prompt(make_default_question)['make_default']
                if make_default:
                    update_ssh_config(username, make_default=True)
            else:
                if not is_default_account_set():
                    make_default = prompt(make_default_question)['make_default']
                    if make_default:
                        update_ssh_config(username, make_default=True)
                else:
                    update_ssh_config(username)  # it adds the new account to SSH config

    list_accounts(load_accounts_from_config())  # Reload accounts to include the newly added one
