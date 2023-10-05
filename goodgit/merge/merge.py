import subprocess
import requests
import json
import questionary
from rich import print

from goodgit.utils import is_git_repo

def branch_exists(branch):
    try:
        subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_conflict_and_context(file_path):
    conflict_and_context = ""
    conflict_start = None
    conflict_end = None
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "<<<<<<< HEAD" in line:
                conflict_start = i
            if ">>>>>>>" in line:
                conflict_end = i
                break
        if conflict_start is not None and conflict_end is not None:
            upper_bound = max(0, conflict_start - 100)
            lower_bound = min(len(lines), conflict_end + 100)
            conflict_and_context = "".join(lines[upper_bound:lower_bound])
    return conflict_and_context, conflict_start, conflict_end

def get_conflicted_files():
    result = subprocess.run(["git", "status"], capture_output=True, text=True)
    output = result.stdout.split('\n')
    conflicted_files = []
    for line in output:
        if "both modified:" in line:
            conflicted_files.append(line.split(":")[1].strip())
    return conflicted_files

def resolve_conflicts_in_file(file_path):
    print(f"[yellow]Resolving conflicts in {file_path}...[/yellow]")
    
    conflict_and_context, conflict_start, conflict_end = get_conflict_and_context(file_path)
    
    payload = json.dumps({
        "conflict_and_context": conflict_and_context,
    })

    headersList = {
        "Accept": "*/*",
        "User-Agent": "GoodGit",
        "Content-Type": "application/json",
    }

    reqUrl = "https://orca-app-qmx5i.ondigitalocean.app/api/merge/"
    response = requests.request("POST", reqUrl, data=payload,  headers=headersList)

    if response.status_code == 200:
        resolved_code = response.json()
        print(f"[orange1]{resolved_code['explanation']}[/orange1]")
        print("")
        print(f"[turquoise2]{resolved_code['code']}[/turquoise2]")

        merge_choice = questionary.confirm("Do you want to apply this merge resolution?").ask()
        if merge_choice:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            lines = lines[:conflict_start] + [resolved_code['code']] + lines[conflict_end+1:]
            with open(file_path, 'w') as f:
                f.writelines(lines)
            print(f"[green]Successfully resolved conflicts in {file_path}![/green]")
    else:
        print("[red]API call failed. Exiting.[/red]")


def merge_branches(from_branch=None, to_branch=None):
    if not is_git_repo():
        print("[red]Not a git repository. Exiting.[/red]")
        return

    if not from_branch and not to_branch:
        from_branch = questionary.text("Which branch do you want to merge from?").ask()
        to_branch = questionary.text("Which branch do you want to merge into?").ask()

    if not branch_exists(from_branch) or not branch_exists(to_branch):
        print("[red]One or both branches do not exist. Exiting.[/red]")
        return

    stash_choice = True
    if stash_choice:
        subprocess.run(["git", "stash"])

    subprocess.run(["git", "checkout", to_branch])
    subprocess.run(["git", "merge", from_branch])

    conflicted_files = get_conflicted_files()
    if not conflicted_files:
        print("[green]No conflicts found. You're good to go![/green]")
        return

    for file_path in conflicted_files:
        resolve_conflicts_in_file(file_path)
            
