
import os
import subprocess
import logging
from app.logging_utils import LoggingUtils

class AnsibleUtils:
    def __init__(self, inventory_path=None):
        self.inventory_path = inventory_path or os.getenv('ANSIBLE_INVENTORY', '/etc/ansible/hosts')
        self.logger = LoggingUtils()
        
    def run_playbook(self, playbook_path, extra_vars=None):
        """
        Run an Ansible playbook with optional extra variables.
        
        :param playbook_path: The path to the Ansible playbook file.
        :param extra_vars: A dictionary of extra variables to pass to the playbook (optional).
        :return: stdout and stderr from the Ansible playbook execution.
        """
        if not os.path.exists(playbook_path):
            self.logger.log_action(f"Playbook not found: {playbook_path}", "ERROR")
            raise FileNotFoundError(f"Playbook file '{playbook_path}' does not exist.")
        
        command = ['ansible-playbook', playbook_path, '-i', self.inventory_path]
        
        # Add extra vars if provided
        if extra_vars:
            extra_vars_str = ' '.join(f"{k}={v}" for k, v in extra_vars.items())
            command.extend(['--extra-vars', extra_vars_str])
        
        try:
            self.logger.log_action(f"Running Ansible playbook: {playbook_path}", "INFO")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            self.logger.log_action(f"Playbook {playbook_path} executed successfully", "INFO")
            return result.stdout, result.stderr
        
        except subprocess.CalledProcessError as e:
            self.logger.log_action(f"Ansible playbook {playbook_path} failed: {e.stderr}", "ERROR")
            raise Exception(f"Failed to execute playbook '{playbook_path}': {e.stderr}")

    def ping_inventory(self):
        """
        Ping all hosts in the Ansible inventory to check connectivity.
        
        :return: stdout and stderr from the Ansible ping command.
        """
        command = ['ansible', '-i', self.inventory_path, 'all', '-m', 'ping']
        
        try:
            self.logger.log_action("Pinging all hosts in inventory", "INFO")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            self.logger.log_action("Ping to all hosts completed successfully", "INFO")
            return result.stdout, result.stderr
        
        except subprocess.CalledProcessError as e:
            self.logger.log_action(f"Ansible ping failed: {e.stderr}", "ERROR")
            raise Exception(f"Failed to ping hosts in inventory: {e.stderr}")

    def check_playbook_syntax(self, playbook_path):
        """
        Check the syntax of an Ansible playbook.
        
        :param playbook_path: The path to the Ansible playbook file.
        :return: stdout and stderr from the Ansible syntax check command.
        """
        if not os.path.exists(playbook_path):
            self.logger.log_action(f"Playbook not found: {playbook_path}", "ERROR")
            raise FileNotFoundError(f"Playbook file '{playbook_path}' does not exist.")
        
        command = ['ansible-playbook', '--syntax-check', playbook_path, '-i', self.inventory_path]
        
        try:
            self.logger.log_action(f"Checking syntax for Ansible playbook: {playbook_path}", "INFO")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            self.logger.log_action(f"Syntax check for {playbook_path} completed successfully", "INFO")
            return result.stdout, result.stderr
        
        except subprocess.CalledProcessError as e:
            self.logger.log_action(f"Syntax check failed for {playbook_path}: {e.stderr}", "ERROR")
            raise Exception(f"Syntax check failed for playbook '{playbook_path}': {e.stderr}")

    def list_hosts(self, group_name=None):
        """
        List all hosts in the Ansible inventory, or within a specific group.
        
        :param group_name: The name of the group to list hosts for (optional).
        :return: stdout and stderr from the Ansible inventory command.
        """
        command = ['ansible', '--list-hosts', '-i', self.inventory_path]
        
        if group_name:
            command.append(group_name)
        
        try:
            self.logger.log_action(f"Listing hosts in group: {group_name if group_name else 'all'}", "INFO")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            self.logger.log_action("Host listing completed successfully", "INFO")
            return result.stdout, result.stderr
        
        except subprocess.CalledProcessError as e:
            self.logger.log_action(f"Failed to list hosts: {e.stderr}", "ERROR")
            raise Exception(f"Failed to list hosts: {e.stderr}")
