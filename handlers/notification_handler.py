import requests
import sys
import traceback

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from utils.logger import Logger
from config.config_validation import SENDGRID_API_KEY, SENDGRID_EMAIL_SENDER, PUSHOVER_TOKEN, PUSHOVER_USER, SENDGRID_TARGET_EMAIL


log = Logger('NOTIFICATION HANDLER')

def send_email(title:str, msg:str):
    if not SENDGRID_API_KEY or not SENDGRID_EMAIL_SENDER or not SENDGRID_TARGET_EMAIL:
        raise ValueError('Email notifications disabled. Please provide your SendGrid credentials.')
    
    message = Mail( from_email=SENDGRID_EMAIL_SENDER, to_emails=SENDGRID_TARGET_EMAIL, subject=title, html_content=msg)

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        log.debug(f'Email sent with status code: {response.status_code}, body: {response.body}')

    except Exception as ex:
        errorMessage = ex.__str__()
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        log.debug('Error sending email: ', errorMessage)

def send_pushover(title:str, msg:str):
    if not PUSHOVER_TOKEN or not PUSHOVER_USER:
        raise ValueError('Pushover notifications disabled. Please provide your Pushover credentials.')
    
    try:
        response = requests.post("https://api.pushover.net/1/messages.json", data = {
            "token": PUSHOVER_TOKEN,
            "user": PUSHOVER_USER,
            "title": title,
            "message": msg
        })
        log.debug(f'Pushover sent with status code: {response.status_code}, content: {response.content}')

        
    except Exception as ex:
        errorMessage = ex.__str__()
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        log.debug('Error sending pushover: ', errorMessage)


def send_notification(title:str, msg:str):
    send_email(title,msg)
    send_pushover(title,msg)
