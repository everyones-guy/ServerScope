import unittest
from datetime import datetime
from app import db
from app.models import ScanReport, Server

class TestScanReport(unittest.TestCase):

    def setUp(self):
        """Set up a clean database for each test."""
        db.create_all()

    def tearDown(self):
        """Tear down the database after each test."""
        db.session.remove()
        db.drop_all()

    def test_scan_report_creation(self):
        """Test creating a ScanReport model."""
        scan_report = ScanReport(
            scan_time=datetime.utcnow(),
            total_machines_scanned=20,
            new_machines_count=5,
            report_details="Scan report details here."
        )
        db.session.add(scan_report)
        db.session.commit()

        # Query the scan report back
        queried_report = ScanReport.query.first()
        self.assertIsNotNone(queried_report)
        self.assertEqual(queried_report.total_machines_scanned, 20)
        self.assertEqual(queried_report.new_machines_count, 5)
        self.assertEqual(queried_report.report_details, "Scan report details here.")

    def test_scan_report_with_server_relationship(self):
        """Test creating a ScanReport and associating it with a Server model."""
        # Create a Server
        server = Server(name="Server1", ip="192.168.1.1", os="Linux")
        db.session.add(server)
        db.session.commit()

        # Create a ScanReport and associate it with the server
        scan_report = ScanReport(
            scan_time=datetime.utcnow(),
            total_machines_scanned=15,
            new_machines_count=3,
            report_details="Server scan details.",
            server_id=server.id
        )
        db.session.add(scan_report)
        db.session.commit()

        # Query the scan report and its associated server
        queried_report = ScanReport.query.first()
        self.assertIsNotNone(queried_report)
        self.assertEqual(queried_report.server_id, server.id)
        self.assertEqual(queried_report.report_details, "Server scan details.")
        self.assertEqual(queried_report.server.name, "Server1")

if __name__ == '__main__':
    unittest.main()
