# routes.py

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import Server, Job, ScanReport, AuditLog, db
from app.network_scan_utils import NetworkScanner
from app.command_utils import CommandExecutor
from app.logging_utils import log_action
from app.auth import role_required

main = Blueprint('main', __name__)

@main.route('/servers')
@login_required
def view_servers():
    servers = Server.query.all()
    return render_template('servers.html', servers=servers)

@main.route('/add_server', methods=['POST'])
@login_required
def add_server():
    name = request.form['name']
    ip = request.form['ip']
    os = request.form['os']

    new_server = Server(name=name, ip=ip, os=os)
    db.session.add(new_server)
    db.session.commit()

    log_action(f"Added new server {name} ({ip})", current_user.username)
    return redirect(url_for('main.view_servers'))

@main.route('/execute_command/<server_id>', methods=['GET', 'POST'])
@login_required
def execute_command(server_id):
    server = Server.query.get(server_id)
    if request.method == 'POST':
        command = request.form['command']
        username = request.form['username']
        password = request.form['password']

        # Determine if the server is Linux or Windows and execute the command accordingly
        if server.os.lower() in ['linux', 'debian', 'ubuntu', 'redhat', 'centos']:
            output = CommandExecutor.execute_ssh_command(server.ip, username, password, command)
        elif server.os.lower() in ['windows', 'win']:
            output = CommandExecutor.execute_winrm_command(server.ip, username, password, command)
        else:
            output = "Unsupported OS."

        log_action(f"Executed command on {server.name} ({server.ip}): {command}", current_user.username)
        return render_template('command_result.html', output=output, server=server)

    return render_template('command_form.html', server=server)

@main.route('/scan_network')
@login_required
def scan_network():
    scanner = NetworkScanner(network_range="192.168.1.0/24")
    new_machines, scan_report = scanner.scan_for_ansible_machines()

    log_action(f"Network scan performed by {current_user.username}", current_user.username)
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
    health_output = CommandExecutor.get_server_health(server.ip, server.username, server.password)
    return render_template('server_health.html', server=server, health_output=health_output)

# routes.py
@main.route('/audit_logs')
@role_required('admin')  # Only admins can view logs
def audit_logs():
    logs = AuditLog.query.all()
    return render_template('audit_logs.html', logs=logs)
