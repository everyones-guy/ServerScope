from flask_mail import Mail, Message
import requests
from twilio.rest import Client
import os
from app import app

# Initialize Flask-Mail
mail = Mail(app)

class NotificationUtils:
    @staticmethod
    def send_email(subject, recipients, body, html_body=None):
        """
        Send an email notification.
        - subject: The subject of the email.
        - recipients: List of email recipients.
        - body: The plain-text body of the email.
        - html_body: Optional HTML body for the email.
        """
        try:
            msg = Message(subject, recipients=recipients, body=body)
            if html_body:
                msg.html = html_body
            mail.send(msg)
            print(f"Email sent to {recipients}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    @staticmethod
    def send_slack_message(webhook_url, message):
        """
        Send a notification to a Slack channel.
        - webhook_url: The Slack webhook URL to send the message to.
        - message: The message content.
        """
        try:
            payload = {'text': message}
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                print("Slack message sent successfully.")
            else:
                print(f"Failed to send Slack message: {response.text}")
        except Exception as e:
            print(f"Failed to send Slack message: {e}")

    @staticmethod
    def send_sms(to_phone, body):
        """
        Send an SMS notification using Twilio.
        - to_phone: The recipient's phone number.
        - body: The message body.
        """
        try:
            account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
            auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
            from_phone = os.environ.get('TWILIO_PHONE_NUMBER')

            client = Client(account_sid, auth_token)
            message = client.messages.create(
                to=to_phone,
                from_=from_phone,
                body=body
            )
            print(f"SMS sent to {to_phone}: {message.sid}")
        except Exception as e:
            print(f"Failed to send SMS: {e}")

