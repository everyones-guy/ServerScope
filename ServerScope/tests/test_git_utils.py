import unittest
from unittest.mock import patch, MagicMock
from app.git_utils import GitUtils
import git

class TestGitUtils(unittest.TestCase):

    @patch('git.Repo.clone_from')
    def test_clone_repository_success(self, mock_clone_from):
        """Test cloning a Git repository successfully."""
        # Simulate successful cloning
        mock_repo = MagicMock()
        mock_clone_from.return_value = mock_repo
        
        # Call the function
        result = GitUtils.clone_repository('https://github.com/user/repo.git', '/path/to/destination')
        
        # Assertions
        mock_clone_from.assert_called_with('https://github.com/user/repo.git', '/path/to/destination')
        self.assertTrue(result)
        
    @patch('git.Repo.clone_from')
    def test_clone_repository_failure(self, mock_clone_from):
        """Test cloning a Git repository with failure."""
        # Simulate a cloning failure
        mock_clone_from.side_effect = git.GitError("Cloning failed")
        
        # Call the function
        result = GitUtils.clone_repository('https://github.com/user/repo.git', '/path/to/destination')
        
        # Assertions
        mock_clone_from.assert_called_with('https://github.com/user/repo.git', '/path/to/destination')
        self.assertFalse(result)

    @patch('git.Repo')
    def test_pull_latest_changes_success(self, mock_repo):
        """Test pulling the latest changes from a Git repository."""
        # Setup mock repo and simulate successful pull
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        mock_origin = MagicMock()
        mock_repo_instance.remotes.origin = mock_origin
        mock_origin.pull.return_value = "Successfully pulled"
        
        # Call the function
        result = GitUtils.pull_latest_changes('/path/to/repo')
        
        # Assertions
        mock_repo.assert_called_with('/path/to/repo')
        mock_origin.pull.assert_called_once()
        self.assertEqual(result, "Successfully pulled")

    @patch('git.Repo')
    def test_pull_latest_changes_failure(self, mock_repo):
        """Test pulling the latest changes from a Git repository with failure."""
        # Setup mock repo and simulate pull failure
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        mock_origin = MagicMock()
        mock_repo_instance.remotes.origin = mock_origin
        mock_origin.pull.side_effect = git.GitError("Pull failed")
        
        # Call the function
        result = GitUtils.pull_latest_changes('/path/to/repo')
        
        # Assertions
        mock_repo.assert_called_with('/path/to/repo')
        mock_origin.pull.assert_called_once()
        self.assertEqual(result, "Error: Pull failed")

    @patch('git.Repo')
    def test_commit_changes_success(self, mock_repo):
        """Test committing changes to a Git repository successfully."""
        # Setup mock repo and simulate successful commit
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        mock_repo_instance.git.commit.return_value = "Successfully committed"
        
        # Call the function
        result = GitUtils.commit_changes('/path/to/repo', 'Test commit message')
        
        # Assertions
        mock_repo.assert_called_with('/path/to/repo')
        mock_repo_instance.git.commit.assert_called_with('-m', 'Test commit message')
        self.assertEqual(result, "Successfully committed")
        
    @patch('git.Repo')
    def test_commit_changes_failure(self, mock_repo):
        """Test committing changes to a Git repository with failure."""
        # Setup mock repo and simulate commit failure
        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        mock_repo_instance.git.commit.side_effect = git.GitError("Commit failed")
        
        # Call the function
        result = GitUtils.commit_changes('/path/to/repo', 'Test commit message')
        
        # Assertions
        mock_repo.assert_called_with('/path/to/repo')
        mock_repo_instance.git.commit.assert_called_with('-m', 'Test commit message')
        self.assertEqual(result, "Error: Commit failed")

if __name__ == '__main__':
    unittest.main()
