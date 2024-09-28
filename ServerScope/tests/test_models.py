import unittest
from app import db
from app.models import Server, Job, AuditLog
from datetime import datetime

class TestModels(unittest.TestCase):

    def setUp(self):
        """Set up a clean database for each test."""
        db.create_all()

    def tearDown(self):
        """Tear down the database after each test."""
        db.session.remove()
        db.drop_all()

    def test_server_creation(self):
        """Test creating a Server model."""
        server = Server(name="TestServer", ip="192.168.1.1", os="Linux")
        db.session.add(server)
        db.session.commit()

        # Query the server back
        queried_server = Server.query.first()
        self.assertIsNotNone(queried_server)
        self.assertEqual(queried_server.name, "TestServer")
        self.assertEqual(queried_server.ip, "192.168.1.1")
        self.assertEqual(queried_server.os, "Linux")

    def test_job_creation(self):
        """Test creating a Job model."""
        job = Job(description="Test Job", status="Running", scheduled_time=datetime.utcnow())
        db.session.add(job)
        db.session.commit()

        # Query the job back
        queried_job = Job.query.first()
        self.assertIsNotNone(queried_job)
        self.assertEqual(queried_job.description, "Test Job")
        self.assertEqual(queried_job.status, "Running")

    def test_audit_log_creation(self):
        """Test creating an AuditLog model."""
        audit_log = AuditLog(action="User logged in", user="test_user", timestamp=datetime.utcnow())
        db.session.add(audit_log)
        db.session.commit()

        # Query the audit log back
        queried_audit_log = AuditLog.query.first()
        self.assertIsNotNone(queried_audit_log)
        self.assertEqual(queried_audit_log.action, "User logged in")
        self.assertEqual(queried_audit_log.user, "test_user")

if __name__ == '__main__':
    unittest.main()
