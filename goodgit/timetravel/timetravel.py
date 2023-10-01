import os
import tempfile
import git
import questionary
from rich import print

def read_from_file(file_path):
    """Read content from a file."""
    with open(file_path, 'r') as f:
        return f.read().strip()

def write_to_file(file_path, content):
    """Write content to a file."""
    with open(file_path, 'w') as f:
        f.write(content)

def get_default_branch(repo):
    """Get the default branch of the repository."""
    return repo.git.rev_parse("--abbrev-ref", "origin/HEAD").split('/')[-1]

def timetravel():
    """
    Perform Git "time-travel" by allowing the user to checkout to any commit.
    """
    # Initialize temp dir and config file
    temp_dir = tempfile.gettempdir()
    config_file = os.path.join(temp_dir, 'goodgit_time_travel_config.conf')

    # Initialize GitPython repo object
    repo = git.Repo(os.getcwd())

    # Check if HEAD is detached
    is_detached = repo.head.is_detached
    current_branch = ""

    if is_detached:
        if os.path.exists(config_file):
            current_branch = read_from_file(config_file)
        else:
            # Switch to default branch
            default_branch = get_default_branch(repo)
            repo.git.checkout(default_branch)
            current_branch = default_branch
    else:
        current_branch = repo.active_branch.name
        write_to_file(config_file, current_branch)

    # Checkout to the current branch
    repo.git.checkout(current_branch)

    # Check if the latest commit is already 'LATEST_CODE_STATE'
    latest_commit_message = next(repo.iter_commits()).message.strip()

    if latest_commit_message != 'LATEST_CODE_STATE':
        # Create temp commit only if the latest is not already 'LATEST_CODE_STATE'
        repo.git.add('-A')
        repo.git.commit('--allow-empty', '-m', 'LATEST_CODE_STATE')

    # Get list of commit titles (first line of each commit message)
    commit_titles = [commit.message.strip().split('\n')[0] for commit in repo.iter_commits()]

    # Use Questionary to show commits to user
    selected_commit_title = questionary.select(
        "Which commit would you like to checkout?",
        choices=commit_titles
    ).ask()

    # If user quits, do nothing
    if selected_commit_title is None:
        return

    # Find the full commit message corresponding to the selected title
    selected_commit_message = next(commit.message.strip() for commit in repo.iter_commits() if commit.message.strip().split('\n')[0] == selected_commit_title)

    # Checkout to that commit
    if selected_commit_message == "LATEST_CODE_STATE":
        repo.git.checkout(current_branch)
        repo.git.reset('HEAD~1', '--soft')
        # Unstage all staged changes using GitPython
        repo.index.reset()
    else:
        commit = next(commit for commit in repo.iter_commits() if commit.message.strip() == selected_commit_message)
        repo.git.checkout(commit)

    print("[green]Time travel complete![/green]")