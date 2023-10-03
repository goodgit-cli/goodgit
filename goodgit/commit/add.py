import subprocess

import questionary
from rich import print
from pathlib import Path
from prompt_toolkit.keys import Keys
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import has_selection, Condition
from prompt_toolkit.completion import Completer, Completion

def git_unadd():
    """
    Executes the 'git reset' command to unstage all changes.
    """
    subprocess.run(["git", "reset"])


def validate_files(files):
    """
    Validates the 'files' parameter to ensure it's either None, '*', '.', or a list of strings.
    
    Parameters:
        files (None or str or list): The files to be added to git.
        
    Returns:
        bool: True if the input is valid, False otherwise.
    """
    if files is None:
        return True
    if files in ['*', '.']:
        return True
    if isinstance(files, list) and all(isinstance(f, str) for f in files):
        return True
    return False

def git_add(files):
    """
    Executes the 'git add' command based on the provided files.
    
    Parameters:
        files (str or list): The files to be added to git. '*' or '.' adds all files.
    """
    if files in ['*', '.']:
        subprocess.run(["git", "add", "."])
    else:
        subprocess.run(["git", "add"] + files)


class MultiPathCompleter(Completer):
    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        last_word = text_before_cursor.split(' ')[-1]
        
        if last_word.endswith('/'):
            glob_pattern = f"{last_word}*"
        else:
            glob_pattern = f"{last_word.split('/')[-1]}*"
        
        for path in Path('.').glob(glob_pattern):
            if path.name.startswith(last_word.split('/')[-1]):
                yield Completion(str(path), start_position=-len(last_word))

# Create custom key bindings
kb = KeyBindings()

# Custom filter to check if the completion menu is showing
is_completion_showing = Condition(lambda: bool(session.app.current_buffer.complete_state))

@kb.add(Keys.Enter, filter=is_completion_showing & ~has_selection)
def _(event):
    " Insert space when completion menu is showing but nothing is selected. "
    event.current_buffer.insert_text(' ')

session = PromptSession()

def get_files_to_add():
    completer = MultiPathCompleter()
    files = session.prompt("Enter the files to add (separated by space): ", completer=completer, key_bindings=kb).split()
    return files

def add(files=None):
    """
    Main function to handle the 'git add' operation. It either takes a direct input or asks the user
    for what files to add.
    
    Parameters:
        files (None or str or list, optional): The files to be added to git. Defaults to None.
    """
    # Validate the 'files' parameter
    if not validate_files(files):
        raise ValueError("Invalid 'files' parameter. Must be None, '*', '.', or a list of strings.")
    
    # If 'files' is None, ask the user for input
    if files is None:
        choice = questionary.select(
            "Do you want to add all files or specific files?",
            choices=["All files", "Specific files"]
        ).ask()
        
        if choice == "All files":
            files = "*"
        else:
            # Use path autocomplete for ease of use
            files = get_files_to_add()
    else:
        print("[white]Adding files[/white]")
    
    # Execute the 'git add' command
    git_add(files)

if __name__ == "__main__":
    add()
