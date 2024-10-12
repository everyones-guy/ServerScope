# nfs_utils.py

import os
import paramiko
from app.models import NFSFile, Server, db
from datetime import datetime

class NFSUtils:
    @staticmethod
    def list_nfs_shares(server_ip, username, password):
        """
        List the NFS shares on a remote server.
        - server_ip: IP address of the remote server.
        - username: SSH username.
        - password: SSH password.
        - Returns: A list of dictionaries containing file path, size, and owner.
        """
        command = "showmount -e"  # Command to list NFS shares
        try:
            output = NFSUtils.execute_ssh_command(server_ip, username, password, command)
            if "no exports" in output.lower():
                return []
            return NFSUtils.parse_nfs_output(output)
        except Exception as e:
            print(f"Failed to list NFS shares: {e}")
            return []

    @staticmethod
    def add_nfs_share(server_ip, username, password, share_path, options="rw,sync"):
        """
        Add a new NFS share on a remote server.
        - server_ip: IP address of the remote server.
        - username: SSH username.
        - password: SSH password.
        - share_path: The path to the directory to be shared.
        - options: NFS export options (default: 'rw,sync').
        - Returns: Success or failure message.
        """
        command = f"sudo exportfs -o {options} {share_path}"
        try:
            output = NFSUtils.execute_ssh_command(server_ip, username, password, command)
            return f"NFS share added: {share_path} with options {options}"
        except Exception as e:
            return f"Failed to add NFS share: {e}"

    @staticmethod
    def remove_nfs_share(server_ip, username, password, share_path):
        """
        Remove an existing NFS share from a remote server.
        - server_ip: IP address of the remote server.
        - username: SSH username.
        - password: SSH password.
        - share_path: The path to the directory being shared.
        - Returns: Success or failure message.
        """
        command = f"sudo exportfs -u {share_path}"
        try:
            output = NFSUtils.execute_ssh_command(server_ip, username, password, command)
            return f"NFS share removed: {share_path}"
        except Exception as e:
            return f"Failed to remove NFS share: {e}"

    @staticmethod
    def log_nfs_shares_to_db(server_id, shares):
        """
        Log the NFS shares to the database.
        - server_id: ID of the server in the database.
        - shares: A list of dictionaries containing file path, size, and owner.
        """
        try:
            server = Server.query.get(server_id)
            for share in shares:
                nfs_file = NFSFile(
                    server_id=server_id,
                    file_path=share['path'],
                    size=share['size'],
                    owner=share['owner']
                )
                db.session.add(nfs_file)
            db.session.commit()
            print(f"NFS shares logged for server {server.name}")
        except Exception as e:
            print(f"Failed to log NFS shares to the database: {e}")

    @staticmethod
    def execute_ssh_command(server_ip, username, password, command):
        """
        Execute an SSH command on a remote server.
        - server_ip: IP address of the remote server.
        - username: SSH username.
        - password: SSH password.
        - command: Command to run on the remote server.
        - Returns: The output of the SSH command.
        """
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(server_ip, username=username, password=password)
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            client.close()
            if error:
                return f"Error: {error}"
            return output
        except Exception as e:
            return f"Error connecting to {server_ip}: {str(e)}"

    @staticmethod
    def parse_nfs_output(output):
        """
        Parse the output of the 'showmount -e' command.
        - output: Raw string output of the NFS share listing.
        - Returns: A list of dictionaries containing file path, size, and owner.
        """
        shares = []
        lines = output.splitlines()
        for line in lines[1:]:  # Skip the header
            parts = line.split()
            if len(parts) >= 2:
                share = {
                    'path': parts[0],  # Share path
                    'size': 'Unknown',  # You could add logic to calculate size if needed
                    'owner': 'Unknown'  # Owner info might need another command to determine
                }
                shares.append(share)
        return shares

