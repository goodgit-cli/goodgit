import subprocess

def is_git_repo():
    try:
        subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_git_remote():
    try:
        result = subprocess.run(['git', 'remote', '-v'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stdout:
            return True, result.stdout.split()[1]  # Extracting the remote URL
        else:
            return False, None
    except Exception as e:
        print(f"An error occurred while checking for git remote: {e}")
        return False, None