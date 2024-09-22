import unittest
from app.models import ScanReport, db

class TestScanReports(unittest.TestCase):

    def test_scan_report_storage(self):
        # Create a mock scan report
        report = ScanReport(
            total_machines_scanned=10,
            existing_machines_count=7,
            new_machines_count=3
        )
        db.session.add(report)
        db.session.commit()

        # Check that the report was saved correctly
        saved_report = ScanReport.query.first()
        self.assertEqual(saved_report.total_machines_scanned, 10)
        self.assertEqual(saved_report.existing_machines_count, 7)
        self.assertEqual(saved_report.new_machines_count, 3)

if __name__ == '__main__':
    unittest.main()
