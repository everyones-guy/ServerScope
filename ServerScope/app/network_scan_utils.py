import nmap 
from app.models import Server, NetworkScanResult, db
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(filename='network_scan.log', level=logging.ERROR)
logger = logging.getLogger(__name__)

class NetworkScanner:
    def __init__(self, network_range='192.168.1.0/24'):
        """
        Initialize the network scanner with the network range to scan.
        """
        self.network_range = network_range
        self.scanner = nmap.PortScanner()

    def scan_network(self):
        """
        Perform the network scan using nmap.
        """
        print(f"Scanning network: {self.network_range}")
        try:
            self.scanner.scan(hosts=self.network_range, arguments='-sn')  # Ping scan
            results = []
            for host in self.scanner.all_hosts():
                status = self.scanner[host].state()
                hostname = self.scanner[host].hostname() if self.scanner[host].hostname() else "Unknown"
                results.append({
                    'ip': host,
                    'hostname': hostname,
                    'status': status
                })
            return results
        except Exception as e:
            print(f"Network scan failed: {e}")
            logger.error(f"Network scan failed: {e}")
            return []

    def compare_scan_results(self, scan_results):
        """
        Compare scan results with existing servers in the database.
        """
        existing_machines = 0
        new_machines = 0
        existing_ips = {server.ip_address for server in Server.query.with_entities(Server.ip_address).all()}
        
        for result in scan_results:
            if result['ip'] in existing_ips:
                existing_machines += 1
            else:
                new_machines += 1
                self.add_new_server(result)
        
        return {
            'existing_machines': existing_machines,
            'new_machines': new_machines,
            'total_machines': len(scan_results)
        }

    def add_new_server(self, scan_result):
        """
        Add a new server to the database from the scan result.
        """
        try:
            new_server = Server(
                name=scan_result['hostname'],
                ip_address=scan_result['ip'],
                username="unknown",  
                password="unknown",  
                os_type="unknown",   
                status=scan_result['status']
            )
            db.session.add(new_server)
            db.session.commit()
            print(f"New server added: {new_server.ip_address}")
        except Exception as e:
            print(f"Failed to add new server: {e}")
            logger.error(f"Failed to add new server: {e}")

    def log_scan_results(self, scan_data):
        """
        Log the scan results in the database for historical tracking.
        """
        try:
            scan_result = NetworkScanResult(
                scan_time=datetime.utcnow(),
                total_machines_scanned=scan_data['total_machines'],
                existing_machines_count=scan_data['existing_machines'],
                new_machines_count=scan_data['new_machines']
            )
            db.session.add(scan_result)
            db.session.commit()
            print(f"Network scan results logged: {scan_result.scan_time}")
        except Exception as e:
            print(f"Failed to log scan results: {e}")
            logger.error(f"Failed to log scan results: {e}")

    def run_scan_and_store_results(self):
        """
        Run a full network scan, compare results, and store the results.
        """
        scan_results = self.scan_network()
        comparison = self.compare_scan_results(scan_results)
        self.log_scan_results(comparison)
        print(f"Scan complete. Existing machines: {comparison['existing_machines']}, New machines: {comparison['new_machines']}.")
        return comparison
