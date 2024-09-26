
import unittest
from flask import url_for
from app import create_app, db
from app.models import User, Server
from flask_login import current_user
from unittest.mock import patch


class TestRoutes(unittest.TestCase):

    def setUp(self):
        """Set up the test application and database."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for tests
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

        # Create tables in the test database
        db.create_all()

        # Set up some test data (users, servers, etc.)
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('testpassword')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        """Tear down the test application and database."""
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def login(self, username, password):
        """Helper method to log in a user."""
        return self.client.post('/auth/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        """Helper method to log out a user."""
        return self.client.get('/auth/logout', follow_redirects=True)

    def test_homepage(self):
        """Test if the homepage loads successfully."""
        response = self.client.get(url_for('main.index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_about_page(self):
        """Test if the about page loads successfully."""
        response = self.client.get(url_for('main.about'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'About', response.data)

    def test_login_logout(self):
        """Test login and logout functionality."""
        # Log in with valid credentials
        response = self.login('testuser', 'testpassword')
        self.assertIn(b'Login successful', response.data)
        self.assertTrue(current_user.is_authenticated)

        # Log out
        response = self.logout()
        self.assertIn(b'You have been logged out', response.data)
        self.assertFalse(current_user.is_authenticated)

    def test_view_servers_requires_login(self):
        """Test that the view_servers page requires user login."""
        response = self.client.get(url_for('main.view_servers'), follow_redirects=True)
        self.assertIn(b'Please log in to access this page', response.data)

    @patch('app.routes.CommandExecutor.execute_ssh_command')
    def test_execute_command(self, mock_execute):
        """Test the execute command route for servers."""
        # Log in first
        self.login('testuser', 'testpassword')

        # Add a test server to the database
        server = Server(name='test_server', ip='192.168.1.1', os='Linux')
        db.session.add(server)
        db.session.commit()

        # Mock the SSH command execution
        mock_execute.return_value = 'Command output'

        response = self.client.post(url_for('main.execute_command', server_id=server.id), data=dict(
            command='ls',
            username='root',
            password='rootpassword'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Command executed on server test_server', response.data)

    @patch('app.routes.NetworkScanner.scan_for_ansible_machines')
    def test_scan_network(self, mock_scan):
        """Test the network scan route."""
        # Log in first
        self.login('testuser', 'testpassword')

        # Mock the network scanner
        mock_scan.return_value = (['192.168.1.2', '192.168.1.3'], 'Scan Report')

        response = self.client.get(url_for('main.scan_network'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Network scan completed successfully', response.data)

    def test_admin_dashboard_access_control(self):
        """Test that only admins can access the admin dashboard."""
        # Log in first (non-admin user)
        self.login('testuser', 'testpassword')

        # Try to access the admin dashboard as a non-admin user
        response = self.client.get(url_for('main.admin_dashboard'), follow_redirects=True)
        self.assertEqual(response.status_code, 403)  # Forbidden access

    def test_view_scan_reports(self):
        """Test that authenticated users can view network scan reports."""
        # Log in first
        self.login('testuser', 'testpassword')

        response = self.client.get(url_for('main.view_scan_reports'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Scan Reports', response.data)


if __name__ == '__main__':
    unittest.main()
