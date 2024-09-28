from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from notification_utils import NotificationUtils
from backup_utils import run_backup
from command_utils import CommandExecutor
from app import db
from app.models import Server, Job
from datetime import datetime

# Initialize scheduler with job store for persistence
scheduler = BackgroundScheduler()

# Set up SQLAlchemy JobStore for persistent job storage
scheduler.add_jobstore(SQLAlchemyJobStore(url='sqlite:///jobs.db'), 'default')

# Define global notification recipients
NOTIFICATION_EMAILS = ["admin@example.com"]
SLACK_WEBHOOK = "https://hooks.slack.com/services/your/slack/webhook/url"
SMS_NUMBER = "+1234567890"

def scheduled_health_check(server_id):
    """
    Health check for a specific server, identified by server_id.
    Notifies admin if issues are found.
    """
    try:
        server = Server.query.get(server_id)
        if not server:
            raise ValueError(f"Server with ID {server_id} not found.")

        print(f"Running health check on server {server.name} ({server.ip_address})...")
        health_output = CommandExecutor.get_server_health(server.ip_address, server.username, server.password)
        
        # If health check returns any critical issues, notify admins
        if "critical" in health_output.lower():
            NotificationUtils.send_email(
                subject="Critical Server Health Alert",
                recipients=NOTIFICATION_EMAILS,
                body=f"Server {server.name} has reported a critical issue.\n\nDetails:\n{health_output}"
            )
            NotificationUtils.send_slack_message(SLACK_WEBHOOK, f"Critical issue detected on {server.name}.")
            NotificationUtils.send_sms(SMS_NUMBER, f"Critical issue detected on {server.name}.")
        else:
            print(f"Server {server.name} is healthy.")
    except Exception as e:
        print(f"Failed to run health check for server {server_id}: {e}")
        NotificationUtils.send_email(
            subject="Health Check Failure",
            recipients=NOTIFICATION_EMAILS,
            body=f"Health check failed for server {server_id}. Error: {e}"
        )

def scheduled_backup(server_id):
    """
    Backup task for a specific server, identified by server_id.
    Sends notifications on success or failure.
    """
    try:
        server = Server.query.get(server_id)
        if not server:
            raise ValueError(f"Server with ID {server_id} not found.")
        
        print(f"Starting backup for server {server.name} ({server.ip_address})...")
        result = run_backup(server.ip_address, server.username, server.password)

        # Log backup success and notify
        print(f"Backup completed for {server.name}.")
        NotificationUtils.send_email(
            subject="Backup Successful",
            recipients=NOTIFICATION_EMAILS,
            body=f"Backup for server {server.name} completed successfully.\n\nDetails:\n{result}"
        )
        NotificationUtils.send_slack_message(SLACK_WEBHOOK, f"Backup completed successfully for {server.name}.")
    except Exception as e:
        print(f"Backup failed for server {server_id}: {e}")
        NotificationUtils.send_email(
            subject="Backup Failed",
            recipients=NOTIFICATION_EMAILS,
            body=f"Backup for server {server_id} failed. Error: {e}"
        )
        NotificationUtils.send_sms(SMS_NUMBER, f"Backup failed for server {server.name}: {e}")

def log_job_execution(job_id, status, result=None):
    """
    Log the status of a job (e.g., 'Completed', 'Failed') into the database.
    """
    try:
        job = Job.query.get(job_id)
        if job:
            job.status = status
            job.executed_at = datetime.utcnow()
            job.result = result
            db.session.commit()
            print(f"Job {job_id} status updated: {status}")
        else:
            print(f"Job with ID {job_id} not found.")
    except Exception as e:
        print(f"Failed to log job execution for job {job_id}: {e}")

# Function to add scheduled jobs
def add_health_check_job(server_id, interval_minutes):
    """
    Schedule a recurring health check job for a server.
    - server_id: The ID of the server to run the health check on.
    - interval_minutes: How often to run the health check, in minutes.
    """
    try:
        job = scheduler.add_job(
            scheduled_health_check,
            trigger='interval',
            minutes=interval_minutes,
            args=[server_id],
            id=f'health_check_{server_id}',
            replace_existing=True
        )
        print(f"Health check job scheduled for server {server_id} every {interval_minutes} minutes.")
    except Exception as e:
        print(f"Failed to schedule health check for server {server_id}: {e}")

def add_backup_job(server_id, interval_hours):
    """
    Schedule a recurring backup job for a server.
    - server_id: The ID of the server to run the backup on.
    - interval_hours: How often to run the backup, in hours.
    """
    try:
        job = scheduler.add_job(
            scheduled_backup,
            trigger='interval',
            hours=interval_hours,
            args=[server_id],
            id=f'backup_{server_id}',
            replace_existing=True
        )
        print(f"Backup job scheduled for server {server_id} every {interval_hours} hours.")
    except Exception as e:
        print(f"Failed to schedule backup for server {server_id}: {e}")

# Function to remove jobs
def remove_job(job_id):
    """
    Remove a scheduled job by its ID.
    """
    try:
        scheduler.remove_job(job_id)
        print(f"Job {job_id} removed successfully.")
    except Exception as e:
        print(f"Failed to remove job {job_id}: {e}")

# Start the scheduler
scheduler.start()
print("Scheduler started and ready to execute jobs.")

