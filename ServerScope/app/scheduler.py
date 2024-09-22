# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def scheduled_health_check():
    # Logic to perform regular health checks
    print("Scheduled health check running...")

scheduler.add_job(scheduled_health_check, 'interval', minutes=30)  # Runs every 30 minutes
scheduler.start()
