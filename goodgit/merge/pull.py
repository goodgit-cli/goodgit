import subprocess
from rich import print

from goodgit.utils import is_git_repo
from .merge import branch_exists, get_conflicted_files, resolve_conflicts_in_file

def pull_changes(remote=None, branch=None):
    if not is_git_repo():
        print("[red]Not a git repository. Exiting.[/red]")
        return

    if not remote and not branch:
        remote = "origin"
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
        branch = result.stdout.strip()

    if not branch_exists(branch):
        print("[red]The specified branch does not exist. Exiting.[/red]")
        return

    ff_result = subprocess.run(["git", "pull", "--no-commit", "--ff-only", remote, branch], capture_output=True, text=True)
    
    if ff_result.returncode == 0:
        print("[bold green]Code up-to date[/bold green]")
        return False, []
    else:
        print("[white]Merging with remote code[/white]")
        subprocess.run(["git", "pull", "--no-rebase", "--no-commit", remote, branch])

    conflicted_files = get_conflicted_files()
    if not conflicted_files:
        print("[bold green]No conflicts found. You're good to go![/bold green]")
        return True, conflicted_files

    for file_path in conflicted_files:
        # resolve_conflicts_in_file(file_path)
        print(f"[turquoise2]Resolve conflicts in [bold turquoise2]{file_path}[/bold turquoise2][/turquoise2]")
        
    print("[orange1]Once resolved; run [bold orange1]gg commit[/bold orange1] to commit.[/orange1]")
        
    return False, conflicted_files
