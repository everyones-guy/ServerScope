# notification_utils.py

from flask_mail import Mail, Message
from app import app

mail = Mail(app)

def send_alert(subject, body, recipients):
    msg = Message(subject, sender='noreply@example.com', recipients=recipients)
    msg.body = body
    mail.send(msg)

