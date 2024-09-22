from app.models import Server, ScanReport, db
import nmap
import paramiko
import winrm

class NetworkScanner:
    def __init__(self, network_range="192.168.1.0/24"):
        self.network_range = network_range
        self.scanner = nmap.PortScanner()

    def scan_for_ansible_machines(self):
        """Scan the network for machines with SSH or WinRM open and potentially running Ansible."""
        self.scanner.scan(hosts=self.network_range, arguments='-p 22,5985')

        total_machines = 0
        existing_machines = 0
        new_machines = 0
        new_machine_list = []

        for host in self.scanner.all_hosts():
            total_machines += 1
            if self.machine_exists_in_db(host):
                existing_machines += 1
            else:
                new_machine_list.append(self.create_new_machine_entry(host))
                new_machines += 1

        # Store the scan report
        scan_report = ScanReport(
            total_machines_scanned=total_machines,
            existing_machines_count=existing_machines,
            new_machines_count=new_machines
        )
        db.session.add(scan_report)
        db.session.commit()

        return new_machine_list, scan_report

    def machine_exists_in_db(self, host):
        """Check if a machine with the given IP address already exists in the database."""
        return Server.query.filter_by(ip=host).first() is not None

    def create_new_machine_entry(self, host):
        """Create a new machine entry for machines that are not already in the database."""
        if '22/tcp' in self.scanner[host]['tcp'] and self.scanner[host]['tcp']['22/tcp']['state'] == 'open':
            os_type = 'Linux'
            port = 22
        elif '5985/tcp' in self.scanner[host]['tcp'] and self.scanner[host]['tcp']['5985/tcp']['state'] == 'open':
            os_type = 'Windows'
            port = 5985
        else:
            os_type = 'Unknown'
            port = 'Unknown'

        new_server = Server(name=f'Discovered Machine {host}', ip=host, os=os_type)
        db.session.add(new_server)
        db.session.commit()

        return {
            'ip': host,
            'os': os_type,
            'port': port
        }
