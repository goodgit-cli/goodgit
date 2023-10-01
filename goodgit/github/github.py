import os
import json
import requests
import time
import webbrowser
from rich import print
from urllib.parse import parse_qs

def fetch_github_username(access_token):
    url = "https://api.github.com/user"
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['login']
    else:
        print(f"Failed to fetch GitHub username. HTTP Status Code: {response.status_code}. Raw response: {response.text}")
        return None
    
def store_github_access_token(token, email):
    config_path = os.path.expanduser("~/.ssh/goodgit/")
    os.makedirs(config_path, exist_ok=True)
    token_file_path = f"{config_path}access_tokens.json"
    
    tokens = {}
    if os.path.exists(token_file_path):
        with open(token_file_path, "r") as f:
            tokens = json.load(f)
    
    tokens[email] = token
    
    with open(token_file_path, "w") as f:
        json.dump(tokens, f)
        
def retrieve_github_access_token(email):
    token_file_path = os.path.expanduser("~/.ssh/goodgit/access_tokens.json")
    if os.path.exists(token_file_path):
        with open(token_file_path, "r") as f:
            tokens = json.load(f)
            return tokens.get(email)
    return None

def create_github_repo(access_token, repo_name, is_private):
    headers = {'Authorization': f'token {access_token}'}
    data = {'name': repo_name, 'private': is_private}
    response = requests.post('https://api.github.com/user/repos', headers=headers, json=data)
    if response.status_code == 201:
        return repo_name
    else:
        print(f"Failed to create repository. HTTP Status Code: {response.status_code}. Raw response: {response.text}")
        return None
    
def get_github_username(token):
    url = "https://api.github.com/user"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json().get("name", "Unknown")
    else:
        print("Failed to fetch GitHub username.")
        return None

def get_new_access_token(email):
    access_token = retrieve_github_access_token(email)
    if access_token:
        return access_token
    
    client_id = "5f4d455043e52e4de32c"
    device_code_url = "https://github.com/login/device/code"
    payload = {"client_id": client_id, "scope": "repo write:public_key read:public_key"}
    response = requests.post(device_code_url, data=payload)
    
    if response.status_code != 200:
        print("Failed to initiate GitHub OAuth. Exiting.")
        return None

    data = parse_qs(response.text)
    device_code = data['device_code'][0]
    user_code = data['user_code'][0]
    verification_uri = data['verification_uri'][0]
    expires_in = int(data['expires_in'][0])
    interval = int(data['interval'][0])

    print(f"Please go to [bold yellow]{verification_uri}[/bold yellow] and enter this code: [bold yellow]{user_code}[/bold yellow]")
    time.sleep(2)
    webbrowser.open(verification_uri)

    timeout_counter = 0
    token_url = "https://github.com/login/oauth/access_token"
    
    while timeout_counter < expires_in:
        payload = {
            "client_id": client_id,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }
        response = requests.post(token_url, data=payload)
        
        if response.status_code == 200:
            data = parse_qs(response.text)
            if 'access_token' in data:
                access_token = data['access_token'][0]
                store_github_access_token(access_token, email)
                print(f"Your access token is: {access_token}")
                return access_token

        time.sleep(interval)
        timeout_counter += interval

    print("Failed to get access token within the allowed time.")
    return None


def add_ssh_key_to_github(token, title, key):
    url = "https://api.github.com/user/keys"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    payload = {"title": title, "key": key}
    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 201:
        print("SSH key added successfully.")