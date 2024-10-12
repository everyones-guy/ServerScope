# logging_utils.py

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from app.models import AuditLog, db

class LoggingUtils:
    def __init__(self, log_file="app.log", log_level=logging.INFO, max_size=1000000, backup_count=5):
        """
        Initializes the logging utility. By default, logs will be written to `app.log`.
        - log_file: The file where logs will be written.
        - log_level: The logging level (e.g., logging.DEBUG, logging.INFO).
        - max_size: Maximum size of the log file in bytes before it gets rotated.
        - backup_count: Number of backup log files to keep.
        """
        self.logger = logging.getLogger("ServerScopeLogger")
        self.logger.setLevel(log_level)
        
        # Create a rotating file handler to log to a file, with rotation
        handler = RotatingFileHandler(log_file, maxBytes=max_size, backupCount=backup_count)
        handler.setLevel(log_level)

        # Create a console handler to log to stdout
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(handler)
        self.logger.addHandler(console_handler)

    def log_action(self, action_description, username):
        """Log user actions into the AuditLog table."""
        try:
            new_log = AuditLog(
                action=action_description,
                username=username,
                timestamp=datetime.utcnow()
            )
            db.session.add(new_log)
            db.session.commit()
            print(f"Action logged: {action_description} by {username}")
        except Exception as e:
            db.session.rollback()  # Roll back the transaction in case of failure
            print(f"Failed to log action: {e}")

    def log_info(self, message):
        """Logs an info message."""
        self.logger.info(message)
    
    def log_warning(self, message):
        """Logs a warning message."""
        self.logger.warning(message)

    def log_error(self, message):
        """Logs an error message."""
        self.logger.error(message)
    
    def log_debug(self, message):
        """Logs a debug message."""
        self.logger.debug(message)

    def log_to_database(self, action, username):
        """
        Logs a user action to the database.
        - action: The action or message to log.
        - username: The user performing the action.
        """
        try:
            log_entry = AuditLog(action=action, username=username, timestamp=datetime.utcnow())
            db.session.add(log_entry)
            db.session.commit()
            self.logger.info(f"Action logged to database: {action} by {username}")
        except Exception as e:
            self.logger.error(f"Failed to log action to database: {e}")

    def log_exception(self, ex, username=None):
        """
        Logs an exception with an optional username context.
        - ex: The exception to log.
        - username: The user (if available) that encountered the exception.
        """
        message = f"Exception occurred: {ex}"
        if username:
            message += f" | User: {username}"
        self.logger.exception(message)
    
    def log_system_event(self, event_type, message):
        """
        Logs a system-level event (e.g., server health check, backup completed).
        - event_type: Type of event (e.g., "health_check", "backup", "server_error").
        - message: Additional details about the event.
        """
        self.logger.info(f"System Event: {event_type} - {message}")
