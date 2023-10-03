import subprocess
from rich import print

def initialize_git_repo():
    try:
        # Initialize a new git repository
        subprocess.run(['git', 'init'], check=True, text=True)

        # Rename the default branch to "main"
        subprocess.run(['git', 'branch', '-M', 'main'], check=True, text=True)
        
        print("[orange1]Repository initialized and main branch set to 'main'.[/orange1]")
        return True

    except subprocess.CalledProcessError as e:
        print(f"[red]An error occurred: {e}[/red]")
        return False
