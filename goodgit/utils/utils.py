import platform
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
    
def get_detailed_os_name():
    system_name = platform.system()
    if system_name == "Linux":
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro = line[3:].strip().replace('"', '')
                        return f"{distro}_os"
        except FileNotFoundError:
            return "linux_os"
    elif system_name == "Darwin":
        return "mac_os"
    elif system_name == "Windows":
        return f"windows{platform.release()}_os"
    else:
        return "unknown_os"