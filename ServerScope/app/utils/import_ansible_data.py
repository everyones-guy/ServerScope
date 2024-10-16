
import os
import yaml
from app import db
from app.models import Server
from app.logging_utils import LoggingUtils  # Import the LoggingUtils class
import sys

# Instantiate LoggingUtils
logger = LoggingUtils()

def load_ansible_inventory(inventory_file):
    """Load an Ansible inventory file in YAML format and parse it."""
    if not os.path.exists(inventory_file):
        logger.log_action(f"Error: Inventory file '{inventory_file}' not found.", "system")
        return None

    try:
        with open(inventory_file, 'r') as f:
            inventory_data = yaml.safe_load(f)
        return inventory_data
    except yaml.YAMLError as exc:
        logger.log_action(f"Error loading YAML file: {exc}", "system")
        return None
    except Exception as e:
        logger.log_action(f"Unexpected error: {e}", "system")
        return None

def import_servers_from_inventory(inventory_data):
    """Import servers from parsed Ansible inventory data into the database."""
    if not inventory_data:
        logger.log_action("No inventory data to process.", "system")
        return

    imported_servers = 0
    existing_servers = 0

    for group_name, group_data in inventory_data.items():
        if 'hosts' in group_data:
            for host, host_data in group_data['hosts'].items():
                # Extract server details
                ip_address = host_data.get('ansible_host', host)
                os_type = host_data.get('ansible_os_family', 'Unknown')

                # Check if the server already exists in the database
                existing_server = Server.query.filter_by(ip=ip_address).first()
                if existing_server:
                    existing_servers += 1
                    logger.log_action(f"Server '{host}' already exists in the database.", "system")
                else:
                    # Create a new server entry
                    new_server = Server(name=host, ip=ip_address, os=os_type)
                    try:
                        db.session.add(new_server)
                    except Exception as e:
                        db.session.rollback()
                        logger.log_action(f"Error committing server '{host}' to the database: {e}", "system")
                    else:
                        imported_servers += 1
                        logger.log_action(f"Imported new server '{host}' (IP: {ip_address}, OS: {os_type}).", "system")

    # Commit all new servers in one batch
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.log_action(f"Error during final commit: {e}", "system")

    # Log action for importing servers
    logger.log_action(f"Imported {imported_servers} new servers. {existing_servers} already existed.", "import_ansible_data")

    print(f"\nSummary: {imported_servers} new servers imported, {existing_servers} already existed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_ansible_data.py <inventory_file.yaml>")
        sys.exit(1)

    inventory_file = sys.argv[1]
    logger.log_action(f"Loading Ansible inventory from '{inventory_file}'...", "system")

    inventory_data = load_ansible_inventory(inventory_file)
    if inventory_data:
        import_servers_from_inventory(inventory_data)
    else:
        logger.log_action("Failed to load inventory data.", "system")

