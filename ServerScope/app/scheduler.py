# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from notification_utils import send_alert

scheduler = BackgroundScheduler()

def scheduled_health_check():
    # Logic to perform regular health checks
    print("Scheduled health check running...")

scheduler.add_job(scheduled_health_check, 'interval', minutes=30)  # Runs every 30 minutes
scheduler.start()

# Check server health and trigger alert if issues found
if issue_detected:
    send_alert("Server Health Alert", "Issues found on server X", ["admin@example.com"])
