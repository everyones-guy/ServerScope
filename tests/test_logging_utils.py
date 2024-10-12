import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from app.logging_utils import log_action
from app.models import AuditLog
from app import db

class TestLoggingUtils(unittest.TestCase):

    @patch('app.db.session.add')
    @patch('app.db.session.commit')
    def test_log_action_success(self, mock_commit, mock_add):
        """Test successful logging of an action."""
        # Call the function
        log_action('Test action description', 'test_user')

        # Assertions
        mock_add.assert_called_once()
        mock_commit.assert_called_once()

        # Check that the correct AuditLog object was passed
        audit_log_entry = mock_add.call_args[0][0]
        self.assertIsInstance(audit_log_entry, AuditLog)
        self.assertEqual(audit_log_entry.action, 'Test action description')
        self.assertEqual(audit_log_entry.user, 'test_user')
        self.assertIsInstance(audit_log_entry.timestamp, datetime)

    @patch('app.db.session.rollback')  # Adding rollback mock for failure scenarios
    @patch('app.db.session.add')
    @patch('app.db.session.commit')
    def test_log_action_commit_failure(self, mock_commit, mock_add, mock_rollback):
        """Test logging action when database commit fails."""
        # Simulate a commit failure
        mock_commit.side_effect = Exception("Commit failed")

        # Call
