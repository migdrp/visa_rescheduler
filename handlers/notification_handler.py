# Archivo: notification_handler.py
# Carpeta: /handlers

import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config.config_validation import SENDGRID_API_KEY, SENDGRID_EMAIL_SENDER, PUSHOVER_TOKEN, PUSHOVER_USER, PERSONAL_SITE_USER, PERSONAL_SITE_PASS, PUSH_TARGET_EMAIL, PERSONAL_PUSHER_URL


def send_notification(title, msg):
    # SendGrid
    if SENDGRID_API_KEY and SENDGRID_EMAIL_SENDER and PUSH_TARGET_EMAIL:
        message = Mail(
            from_email=SENDGRID_EMAIL_SENDER,
            to_emails=PUSH_TARGET_EMAIL,
            subject=title,
            html_content=msg)
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
        except Exception as e:
            print(e)

    # Pushover
    if PUSHOVER_TOKEN and PUSHOVER_USER:
        r = requests.post("https://api.pushover.net/1/messages.json", data = {
            "token": PUSHOVER_TOKEN,
            "user": PUSHOVER_USER,
            "title": title,
            "message": msg
        })

    # Personal Site
    if PERSONAL_SITE_USER and PERSONAL_SITE_PASS and PERSONAL_PUSHER_URL:
        r = requests.post(PERSONAL_PUSHER_URL, data = {
            "user": PERSONAL_SITE_USER,
            "pass": PERSONAL_SITE_PASS,
            "title": title,
            "message": msg
        })

# Puedes agregar más funciones relacionadas con notificaciones si es necesario.