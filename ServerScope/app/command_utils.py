import paramiko
import winrm
# revisit this to auto configure the http 85 or 86 depending on the server

class CommandExecutor:

    @staticmethod
    def execute_ssh_command(server_ip, username, password, command):
        """Execute a command on a Linux server via SSH"""
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
            return f"Error connecting to {server_ip} via SSH: {str(e)}"

    @staticmethod
    def execute_winrm_command(server_ip, username, password, command):
        """Execute a command on a Windows server via WinRM"""
        try:
            session = winrm.Session(f'http://{server_ip}:5985/wsman', auth=(username, password))
            result = session.run_cmd(command)
            output = result.std_out.decode('utf-8')
            error = result.std_err.decode('utf-8')
            if error:
                return f"Error: {error}"
            return output
        except Exception as e:
            return f"Error connecting to {server_ip} via WinRM: {str(e)}"

    @staticmethod
    def get_server_health(server_ip, username, password):
        """Retrieve server health via SSH"""
        command = "top -bn1 | grep 'Cpu\\|Mem\\|Swap' && df -h"
        return CommandExecutor.execute_ssh_command(server_ip, username, password, command)
