from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(50), nullable=False, default='user')  # e.g., 'admin', 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Password management
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        return self.role == role

    def __repr__(self):
        return f'<User {self.username}>'

# AuditLog Model for tracking user actions
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AuditLog {self.id} - {self.action} by {self.username}>'

# Server Model for storing server information
class Server(db.Model):
    __tablename__ = 'servers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # To support IPv4 and IPv6
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Store securely
    os_type = db.Column(db.String(50), nullable=False)  # e.g., 'Linux', 'Windows'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_health_check = db.Column(db.DateTime)
    status = db.Column(db.String(50), nullable=True)  # 'Healthy', 'Warning', 'Critical', etc.

    def set_password(self, password):
        """Set a hashed password for SSH/WinRM credentials."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Check the hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<Server {self.name} - {self.ip_address}>'

# Job Model for scheduled jobs (e.g., backups, health checks)
class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String(100), nullable=False)  # 'backup', 'health_check', etc.
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # 'Pending', 'Running', 'Completed', 'Failed'
    schedule_time = db.Column(db.DateTime, nullable=False)
    executed_at = db.Column(db.DateTime, nullable=True)
    result = db.Column(db.Text, nullable=True)  # Store result logs or output

    server = db.relationship('Server', backref='jobs')

    __table_args__ = (db.Index('idx_server_schedule', 'server_id', 'schedule_time'),)

    def __repr__(self):
        return f'<Job {self.id} - {self.job_type} on Server {self.server_id}>'

# Splunk Config Model for storing Splunk integration details
class SplunkConfig(db.Model):
    __tablename__ = 'splunk_configs'

    id = db.Column(db.Integer, primary_key=True)
    server_url = db.Column(db.String(255), nullable=False)
    auth_token = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SplunkConfig {self.server_url}>'

# NFS Files Model for storing details of NFS shared files
class NFSFile(db.Model):
    __tablename__ = 'nfs_files'

    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    owner = db.Column(db.String(80), nullable=False)

    server = db.relationship('Server', backref='nfs_files')

    def __repr__(self):
        return f'<NFSFile {self.file_path} on Server {self.server_id}>'

# Tagging Model for server grouping and tagging
class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Tag {self.name}>'

# Many-to-many relationship between Servers and Tags
server_tags = db.Table('server_tags',
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

# Network Scan Results Model
class NetworkScanResult(db.Model):
    __tablename__ = 'network_scan_results'

    id = db.Column(db.Integer, primary_key=True)
    scan_time = db.Column(db.DateTime, default=datetime.utcnow)
    total_machines_scanned = db.Column(db.Integer, nullable=False)
    existing_machines_count = db.Column(db.Integer, nullable=False)
    new_machines_count = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<NetworkScanResult {self.scan_time} - {self.total_machines_scanned} Machines>'
