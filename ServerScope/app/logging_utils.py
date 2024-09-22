# logging_utils.py
from app.models import AuditLog, db
from datetime import datetime

def log_action(action, username):
    """Log an action performed by a user to the AuditLog."""
    log = AuditLog(action=action, username=username, timestamp=datetime.utcnow())
    db.session.add(log)
    db.session.commit()
