import unittest
from unittest.mock import patch, MagicMock
from app.command_utils import CommandExecutor
import paramiko
import winrm

class TestCommandUtils(unittest.TestCase):

    @patch('paramiko.SSHClient')
    def test_execute_ssh_command_success(self, mock_ssh_client):
        """Test successful SSH command execution."""
        # Setup mock SSH client and its behavior
        mock_ssh_instance = MagicMock()
        mock_ssh_client.return_value = mock_ssh_instance
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"Command executed successfully"
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        mock_ssh_instance.exec_command.return_value = (None, mock_stdout, mock_stderr)

        # Call the function
        result = CommandExecutor.execute_ssh_command("192.168.1.1", "user", "password", "ls")

        # Assertions
        self.assertEqual(result, "Command executed successfully")
        mock_ssh_instance.connect.assert_called_with("192.168.1.1", username="user", password="password")
        mock_ssh_instance.exec_command.assert_called_with("ls")
        mock_ssh_instance.close.assert_called_once()

    @patch('paramiko.SSHClient')
    def test_execute_ssh_command_error(self, mock_ssh_client):
        """Test SSH command execution with an error."""
        # Setup mock SSH client and its behavior
        mock_ssh_instance = MagicMock()
        mock_ssh_client.return_value = mock_ssh_instance
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b""
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"Error: Command failed"
        mock_ssh_instance.exec_command.return_value = (None, mock_stdout, mock_stderr)

        # Call the function
        result = CommandExecutor.execute_ssh_command("192.168.1.1", "user", "password", "ls")

        # Assertions
        self.assertEqual(result, "Error: Error: Command failed")
        mock_ssh_instance.connect.assert_called_with("192.168.1.1", username="user", password="password")
        mock_ssh_instance.exec_command.assert_called_with("ls")
        mock_ssh_instance.close.assert_called_once()

    @patch('paramiko.SSHClient')
    def test_execute_ssh_command_connection_failure(self, mock_ssh_client):
        """Test SSH command execution with connection failure."""
        # Simulate a connection failure
        mock_ssh_instance = MagicMock()
        mock_ssh_client.return_value = mock_ssh_instance
        mock_ssh_instance.connect.side_effect = paramiko.SSHException("Connection failed")

        # Call the function
        result = CommandExecutor.execute_ssh_command("192.168.1.1", "user", "password", "ls")

        # Assertions
        self.assertEqual(result, "Error connecting to 192.168.1.1: Connection failed")
        mock_ssh_instance.connect.assert_called_with("192.168.1.1", username="user", password="password")
        mock_ssh_instance.close.assert_called_once()

    @patch('winrm.Session')
    def test_execute_winrm_command_success(self, mock_winrm_session):
        """Test successful WinRM command execution."""
        # Setup mock WinRM session and its behavior
        mock_session_instance = MagicMock()
        mock_winrm_session.return_value = mock_session_instance
        mock_result = MagicMock()
        mock_result.std_out = b"Command executed successfully"
        mock_result.std_err = b""
        mock_session_instance.run_cmd.return_value = mock_result

        # Call the function
        result = CommandExecutor.execute_winrm_command("192.168.1.100", "Administrator", "password", "dir")

        # Assertions
        self.assertEqual(result, "Command executed successfully")
        mock_winrm_session.assert_called_with('http://192.168.1.100:5985/wsman', auth=("Administrator", "password"))
        mock_session_instance.run_cmd.assert_called_with("dir")

    @patch('winrm.Session')
    def test_execute_winrm_command_error(self, mock_winrm_session):
        """Test WinRM command execution with an error."""
        # Setup mock WinRM session and its behavior
        mock_session_instance = MagicMock()
        mock_winrm_session.return_value = mock_session_instance
        mock_result = MagicMock()
        mock_result.std_out = b""
        mock_result.std_err = b"Error: Command failed"
        mock_session_instance.run_cmd.return_value = mock_result

        # Call the function
        result = CommandExecutor.execute_winrm_command("192.168.1.100", "Administrator", "password", "dir")

        # Assertions
        self.assertEqual(result, "Error: Error: Command failed")
        mock_winrm_session.assert_called_with('http://192.168.1.100:5985/wsman', auth=("Administrator", "password"))
        mock_session_instance.run_cmd.assert_called_with("dir")

    @patch('winrm.Session')
    def test_execute_winrm_command_connection_failure(self, mock_winrm_session):
        """Test WinRM command execution with connection failure."""
        # Simulate a connection failure
        mock_session_instance = MagicMock()
        mock_winrm_session.return_value = mock_session_instance
        mock_winrm_session.side_effect = Exception("Connection failed")

        # Call the function
        result = CommandExecutor.execute_winrm_command("192.168.1.100", "Administrator", "password", "dir")

        # Assertions
        self.assertEqual(result, "Error connecting to 192.168.1.100: Connection failed")
        mock_winrm_session.assert_called_with('http://192.168.1.100:5985/wsman', auth=("Administrator", "password"))

if __name__ == '__main__':
    unittest.main()
