from rich import print
import questionary
import subprocess
from typing import Optional, List

from goodgit.utils import is_git_repo

def ask_for_options(prompt: str, choices: List[str]) -> List[str]:
    return questionary.checkbox(prompt, choices=choices).ask() or []

def git_grep_interactive():
    if not is_git_repo():
        return

    search_term = questionary.text("What is the search term?").ask()
    where = ask_for_options("Where do you want to search?", [
        "Specific file types",
        "Previous commits",
        "Branches",
        "Current code"
    ])

    file_type, commit_hash, branch = None, None, None

    if "Specific file types" in where:
        file_type = questionary.text("Which file types (e.g., py, js, txt)?").ask()
    
    if "Previous commits" in where:
        commit_list = subprocess.getoutput("git log --pretty=format:'%h %s'").split("\n")
        commit_hash = questionary.select("Choose a commit:", choices=commit_list).ask().split()[0]
    
    if "Branches" in where:
        branch_list = subprocess.getoutput("git branch --format '%(refname:short)'").split("\n")
        branch = questionary.select("Choose a branch:", choices=branch_list).ask()

    options = ask_for_options("Select search options:", [
        "Case insensitive",
        "Line number",
        "Count",
        "Context lines",
        "AND terms",
        "OR terms",
        "Show filenames only"
    ])

    and_terms = questionary.text("AND terms (separate by comma):").ask() if "AND terms" in options else None
    or_terms = questionary.text("OR terms (separate by comma):").ask() if "OR terms" in options else None

    print("[bold orange1]Performing your search... Hang tight![/bold orange1]")

    try:
        result = git_grep(
            search_term, 
            "Case insensitive" in options, 
            "Line number" in options,
            "Count" in options,
            file_type,
            commit_hash,
            branch,
            2 if "Context lines" in options else None,
            and_terms,
            or_terms,
            "Show filenames only" in options
        )
        
        if result:
            print("[bold green]Search completed. Here are the results:[/bold green]")
            print(result)
        else:
            print("[bold red]No results found for your query.[/bold red]")

    except subprocess.CalledProcessError as e:
        print(f"[bold red]Oops! An error occurred: {e.stderr}[/bold red]")
    except Exception as e:
        print(f"[bold red]Something unexpected happened: {e}[/bold red]")

def git_grep(search_term: str, case_insensitive: bool = False, line_number: bool = False,
             count: bool = False, file_type: Optional[str] = None, commit_hash: Optional[str] = None, 
             branch: Optional[str] = None, context_lines: Optional[int] = None, 
             and_terms: Optional[str] = None, or_terms: Optional[str] = None, 
             show_filenames: bool = False) -> str:
    cmd = ["git", "grep"]
    
    if case_insensitive:
        cmd.append("-i")
    if line_number:
        cmd.append("-n")
    if count:
        cmd.append("-c")
    if context_lines:
        cmd.append(f"-C {context_lines}")
    if show_filenames:
        cmd.append("-l")
    
    if commit_hash:
        cmd.extend([commit_hash, "--"])
    elif branch:
        cmd.extend([branch, "--"])
    
    if and_terms:
        cmd.extend(["-e", search_term, "--and", "-e", and_terms])
    elif or_terms:
        cmd.extend(["-e", search_term, "--or", "-e", or_terms])
    else:
        cmd.append(search_term)
    
    if file_type:
        cmd.append(f"*.{file_type}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stderr

