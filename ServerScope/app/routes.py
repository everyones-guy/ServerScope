from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user, logout_user, login_user
from app.models import Server, Job, NetworkScanResult as ScanReport, AuditLog, db, User
from app.network_scan_utils import NetworkScanner
from app.command_utils import CommandExecutor
from app.logging_utils import LoggingUtils
from app.auth import role_required
from app.nfs_utils import NFSUtils
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import logging

# Setup logging for general errors
logging.basicConfig(filename='error.log', level=logging.ERROR)
error_logger = logging.getLogger(__name__)

# Create an instance of LoggingUtils for logging actions
action_logger = LoggingUtils()

# Define blueprints
nfs_bp = Blueprint('nfs', __name__)
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')  # Assuming you have an 'index.html' in your templates folder

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/servers')
@login_required
def view_servers():
    if current_user.is_authenticated and current_user.role == 'admin':  # Example role check
        servers = Server.query.all()
        return render_template('servers.html', servers=servers)
    else:
        flash("You do not have permission to view this page.", "danger")
        return redirect(url_for('main.index'))

@main.route('/add_server', methods=['POST'])
@login_required
def add_server():
    name = request.form['name']
    ip = request.form['ip']
    os = request.form['os']

    try:
        new_server = Server(name=name, ip=ip, os=os)
        db.session.add(new_server)
        db.session.commit()
        action_logger.log_action(f"Added new server {name} ({ip})", current_user.username)
        flash(f"Server {name} added successfully!", "success")
    except Exception as e:
        error_logger.error(f"Failed to add server {name}: {e}")
        flash(f"Error adding server {name}. Please check logs.", "danger")

    return redirect(url_for('main.view_servers'))

@main.route('/execute_command/<server_id>', methods=['GET', 'POST'])
@login_required
def execute_command(server_id):
    server = Server.query.get_or_404(server_id)

    if request.method == 'POST':
        command = request.form['command']
        username = request.form['username']
        password = request.form['password']

        try:
            # Determine if the server is Linux or Windows and execute the command accordingly
            if server.os.lower() in ['linux', 'debian', 'ubuntu', 'redhat', 'centos']:
                output = CommandExecutor.execute_ssh_command(server.ip, username, password, command)
            elif server.os.lower() in ['windows', 'win']:
                output = CommandExecutor.execute_winrm_command(server.ip, username, password, command)
            else:
                output = "Unsupported or unrecognized OS. Please check the server configuration."

            action_logger.log_action(f"Executed command on {server.name} ({server.ip}): {command}", current_user.username)
            flash(f"Command executed on server {server.name}.", "success")
        except Exception as e:
            error_logger.error(f"Error executing command on {server.name}: {e}")
            flash(f"Failed to execute command. Please check logs.", "danger")

        return render_template('command_result.html', output=output, server=server)

    return render_template('command_form.html', server=server)

@main.route('/scan_network')
@login_required
def scan_network():
    try:
        scanner = NetworkScanner(network_range="192.168.1.0/24")
        new_machines, scan_report = scanner.scan_for_ansible_machines()
        action_logger.log_action(f"Network scan performed by {current_user.username}", current_user.username)
        flash(f"Network scan completed successfully.", "success")
    except Exception as e:
        error_logger.error(f"Error performing network scan: {e}")
        flash(f"Network scan failed. Please check logs.", "danger")

    return render_template('scan_results.html', new_machines=new_machines, report=scan_report)

@main.route('/scan_reports')
@login_required
def view_scan_reports():
    scan_reports = ScanReport.query.order_by(ScanReport.scan_time.desc()).all()
    return render_template('scan_reports.html', scan_reports=scan_reports)

@main.route('/admin')
@role_required('admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@main.route('/user')
@role_required('user')
def user_dashboard():
    return render_template('user_dashboard.html')

@main.route('/server/<int:server_id>/health')
@role_required('admin')  # Restrict access to admins or specific roles
def server_health(server_id):
    server = Server.query.get_or_404(server_id)

    try:
        health_output = CommandExecutor.get_server_health(server.ip, server.username, server.password)
        flash(f"Health check completed for server {server.name}.", "success")
    except Exception as e:
        error_logger.error(f"Error checking health of server {server.name}: {e}")
        flash(f"Health check failed. Please check logs.", "danger")

    return render_template('server_health.html', server=server, health_output=health_output)

@main.route('/audit_logs')
@role_required('admin')  # Only admins can view logs
def audit_logs():
    logs = AuditLog.query.all()
    return render_template('audit_logs.html', logs=logs)

@nfs_bp.route('/nfs/list/<int:server_id>')
@login_required
def list_nfs_shares(server_id):
    server = Server.query.get_or_404(server_id)

    try:
        nfs_shares = NFSUtils.list_nfs_shares(server.ip_address, server.username, server.password)
        NFSUtils.log_nfs_shares_to_db(server_id, nfs_shares)
        flash(f"NFS shares listed for server {server.name}.", "success")
    except Exception as e:
        error_logger.error(f"Error listing NFS shares for server {server.name}: {e}")
        flash(f"Failed to list NFS shares. Please check logs.", "danger")

    return render_template('nfs_shares.html', shares=nfs_shares)

@nfs_bp.route('/nfs/add/<int:server_id>/<path:share_path>')
@login_required
def add_nfs_share(server_id, share_path):
    server = Server.query.get_or_404(server_id)

    try:
        result = NFSUtils.add_nfs_share(server.ip_address, server.username, server.password, share_path)
        flash(result, "success")
    except Exception as e:
        error_logger.error(f"Error adding NFS share {share_path} for server {server.name}: {e}")
        flash(f"Failed to add NFS share. Please check logs.", "danger")

    return redirect(url_for('nfs.list_nfs_shares', server_id=server_id))

@nfs_bp.route('/nfs/remove/<int:server_id>/<path:share_path>')
@login_required
def remove_nfs_share(server_id, share_path):
    server = Server.query.get_or_404(server_id)

    try:
        result = NFSUtils.remove_nfs_share(server.ip_address, server.username, server.password, share_path)
        flash(result, "success")
    except Exception as e:
        error_logger.error(f"Error removing NFS share {share_path} for server {server.name}: {e}")
        flash(f"Failed to remove NFS share. Please check logs.", "danger")

    return redirect(url_for('nfs.list_nfs_shares', server_id=server_id))

@main.route('/setup_database', methods=['GET', 'POST'])
def setup_database():
    if request.method == 'POST':
        db_type = request.form.get('db_type')
        connection_string = request.form.get('connection_string')

        try:
            # Create a database engine depending on the selected type
            if db_type == 'sqlite':
                engine = create_engine(f"sqlite:///{connection_string}")
            elif db_type == 'mysql':
                engine = create_engine(f"mysql+pymysql://{connection_string}")
            elif db_type == 'postgresql':
                engine = create_engine(f"postgresql://{connection_string}")

            db.create_all(bind=engine)
            flash("Database setup completed successfully!", "success")
        except OperationalError as e:
            error_logger.error(f"Database setup failed: {e}")
            flash(f"Failed to set up the database. Please check logs.", "danger")

    return render_template('setup_database.html')

@main.route('/splunk_logs')
@login_required
def splunk_logs():
    # Add logic here for retrieving Splunk logs
    return render_template('splunk_logs.html')  # Ensure you have a 'splunk_logs.html' template
