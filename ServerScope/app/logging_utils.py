import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from app.models import AuditLog, db  # Assuming your models file has these classes

class LoggingUtils:
    def __init__(self, log_file="app.log", log_level=logging.INFO, max_size=1000000, backup_count=5):
        """
        Initializes the logging utility. By default, logs will be written to `app.log`.
        """
        self.logger = logging.getLogger("ServerScopeLogger")
        self.logger.setLevel(log_level)
        
        # Create a rotating file handler to log to a file
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
        """
        Log user actions into the AuditLog table.
        """
        try:
            new_log = AuditLog(
                action=action_description,
                username=username,
                timestamp=datetime.utcnow()
            )
            db.session.add(new_log)
            db.session.commit()
            self.logger.info(f"Action logged: {action_description} by {username}")
        except Exception as e:
            db.session.rollback()  # Roll back in case of failure
            self.logger.error(f"Failed to log action: {e}")
    
    # Other logging methods
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
