import unittest
from unittest.mock import patch, mock_open, MagicMock
import yaml
from app import db
from app.models import Server
from migrations.versions.import_ansible_data import load_ansible_inventory, import_servers_from_inventory

class TestAnsibleUtils(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data="hosts:\n  server1:\n    ansible_host: 192.168.1.1\n    ansible_os_family: Linux")
    def test_load_ansible_inventory_success(self, mock_file):
        """Test loading a valid Ansible inventory file."""
        inventory_data = load_ansible_inventory('dummy_inventory.yaml')
        self.assertIsNotNone(inventory_data)
        self.assertIn('hosts', inventory_data)
        self.assertIn('server1', inventory_data['hosts'])
        self.assertEqual(inventory_data['hosts']['server1']['ansible_host'], '192.168.1.1')

    @patch('builtins.open', new_callable=mock_open)
    def test_load_ansible_inventory_file_not_found(self, mock_file):
        """Test loading a non-existing Ansible inventory file."""
        mock_file.side_effect = FileNotFoundError
        inventory_data = load_ansible_inventory('non_existent_file.yaml')
        self.assertIsNone(inventory_data)

    @patch('yaml.safe_load', side_effect=yaml.YAMLError("YAML error"))
    @patch('builtins.open', new_callable=mock_open)
    def test_load_ansible_inventory_yaml_error(self, mock_file, mock_safe_load):
        """Test loading a YAML file with a YAML error."""
        inventory_data = load_ansible_inventory('invalid_inventory.yaml')
        self.assertIsNone(inventory_data)

    @patch('app.models.Server.query')
    @patch('app.db.session')
    def test_import_servers_from_inventory_new_server(self, mock_db_session, mock_server_query):
        """Test importing a new server from Ansible inventory."""
        # Simulate no existing server in the database
        mock_server_query.filter_by.return_value.first.return_value = None
        
        inventory_data = {
            'hosts': {
                'server1': {
                    'ansible_host': '192.168.1.1',
                    'ansible_os_family': 'Linux'
                }
            }
        }
        
        import_servers_from_inventory(inventory_data)
        
        # Check that the server was added to the session
        self.assertTrue(mock_db_session.add.called)
        self.assertTrue(mock_db_session.commit.called)

    @patch('app.models.Server.query')
    @patch('app.db.session')
    def test_import_servers_from_inventory_existing_server(self, mock_db_session, mock_server_query):
        """Test importing an existing server from Ansible inventory."""
        # Simulate an existing server in the database
        mock_server = MagicMock()
        mock_server_query.filter_by.return_value.first.return_value = mock_server
        
        inventory_data = {
            'hosts': {
                'server1': {
                    'ansible_host': '192.168.1.1',
                    'ansible_os_family': 'Linux'
                }
            }
        }
        
        import_servers_from_inventory(inventory_data)
        
        # Since the server already exists, it should not add a new one
        self.assertFalse(mock_db_session.add.called)
        self.assertTrue(mock_db_session.commit.called)

if __name__ == '__main__':
    unittest.main()
