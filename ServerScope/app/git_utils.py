
import subprocess
import os

class GitUtils:
    @staticmethod
    def clone_repository(repo_url, clone_path):
        """Clone a git repository to a specified path."""
        try:
            if not os.path.exists(clone_path):
                os.makedirs(clone_path)
            command = ["git", "clone", repo_url, clone_path]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                return f"Error cloning repository: {result.stderr}"
            return f"Repository cloned successfully: {result.stdout}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def pull_latest_changes(repo_path, branch="main"):
        """Pull the latest changes from the specified branch in a git repository."""
        try:
            if not os.path.exists(repo_path):
                return f"Repository path does not exist: {repo_path}"
            command = ["git", "-C", repo_path, "pull", "origin", branch]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                return f"Error pulling latest changes: {result.stderr}"
            return f"Latest changes pulled successfully: {result.stdout}"
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def get_git_status(repo_path):
        """Get the status of a git repository."""
        try:
            if not os.path.exists(repo_path):
                return f"Repository path does not exist: {repo_path}"
            command = ["git", "-C", repo_path, "status"]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                return f"Error getting git status: {result.stderr}"
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def checkout_branch(repo_path, branch_name):
        """Checkout a specific branch in the git repository."""
        try:
            if not os.path.exists(repo_path):
                return f"Repository path does not exist: {repo_path}"
            command = ["git", "-C", repo_path, "checkout", branch_name]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                return f"Error checking out branch: {result.stderr}"
            return f"Checked out branch '{branch_name}' successfully: {result.stdout}"
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def create_branch(repo_path, branch_name):
        """Create a new branch in the git repository."""
        try:
            if not os.path.exists(repo_path):
                return f"Repository path does not exist: {repo_path}"
            command = ["git", "-C", repo_path, "checkout", "-b", branch_name]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                return f"Error creating branch: {result.stderr}"
            return f"Branch '{branch_name}' created successfully: {result.stdout}"
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def add_and_commit(repo_path, commit_message):
        """Add all changes and commit with a message in the git repository."""
        try:
            if not os.path.exists(repo_path):
                return f"Repository path does not exist: {repo_path}"
            add_command = ["git", "-C", repo_path, "add", "."]
            commit_command = ["git", "-C", repo_path, "commit", "-m", commit_message]
            
            # Add changes
            result = subprocess.run(add_command, capture_output=True, text=True)
            if result.returncode != 0:
                return f"Error adding changes: {result.stderr}"
            
            # Commit changes
            result = subprocess.run(commit_command, capture_output=True, text=True)
            if result.returncode != 0:
                return f"Error committing changes: {result.stderr}"
            return f"Changes committed successfully: {result.stdout}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def push_changes(repo_path, branch_name="main"):
        """Push committed changes to the remote repository."""
        try:
            if not os.path.exists(repo_path):
                return f"Repository path does not exist: {repo_path}"
            command = ["git", "-C", repo_path, "push", "origin", branch_name]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                return f"Error pushing changes: {result.stderr}"
            return f"Changes pushed to '{branch_name}' branch successfully: {result.stdout}"
        except Exception as e:
            return f"Error: {str(e)}"
