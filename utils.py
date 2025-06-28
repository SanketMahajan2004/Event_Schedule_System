import json
import os
import smtplib
from email.mime.text import MIMEText


def load_events(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return []

def save_events(events, filepath):
    with open(filepath, "w") as f:
        json.dump(events, f, indent=4)



def send_email(subject, message, to_email):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = "your_email_id@gmail.com"
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("your_email_id@gmail.com", "Your_app_password")
        server.send_message(msg)
