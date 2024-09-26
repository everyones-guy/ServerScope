# backup_utils.py
import paramiko
from command_utils import CommandExecutor  # Import CommandExecutor from its module

def run_backup(server_ip, username, password):
    command = "tar -czf /backup/server_backup.tar.gz /important/data"
    try:
        output = CommandExecutor.execute_ssh_command(server_ip, username, password, command)
        return output
    except Exception as e:
        return f"Backup failed: {str(e)}"
