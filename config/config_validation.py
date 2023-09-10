import ast
import configparser

from utils.logger import Logger
from utils.visa_utils import validate_embassies

log = Logger('CONFIG VALIDATION')
config = configparser.ConfigParser()
config.read('./config.ini')


# Personal Info:
USERNAME = config['PERSONAL_INFO']['USERNAME']
PASSWORD = config['PERSONAL_INFO']['PASSWORD']
SCHEDULE_ID = config['PERSONAL_INFO']['SCHEDULE_ID']
PERIOD_START = config['PERSONAL_INFO']['PERIOD_START']
PERIOD_END = config['PERSONAL_INFO']['PERIOD_END']
YOUR_EMBASSIES= ast.literal_eval(config.get("PERSONAL_INFO", "YOUR_EMBASSIES"))

# Notification:
SENDGRID_API_KEY = config['NOTIFICATION']['SENDGRID_API_KEY']
SENDGRID_EMAIL_SENDER = config['NOTIFICATION']['SENDGRID_EMAIL_SENDER']
SENDGRID_TARGET_EMAIL = config['NOTIFICATION']['SENDGRID_TARGET_EMAIL']
PUSHOVER_TOKEN = config['NOTIFICATION']['PUSHOVER_TOKEN']
PUSHOVER_USER = config['NOTIFICATION']['PUSHOVER_USER']

# Time Section:
RETRY_TIME_L_BOUND = config['TIME'].getfloat('RETRY_TIME_L_BOUND')
RETRY_TIME_U_BOUND = config['TIME'].getfloat('RETRY_TIME_U_BOUND')
WORK_LIMIT_TIME = config['TIME'].getfloat('WORK_LIMIT_TIME')
WORK_COOLDOWN_TIME = config['TIME'].getfloat('WORK_COOLDOWN_TIME')
BAN_COOLDOWN_TIME = config['TIME'].getfloat('BAN_COOLDOWN_TIME')
STEP_TIME = config['TIME'].getfloat('STEP_TIME')
SELENIUM_TIMEOUT = config['TIME'].getfloat('SELENIUM_TIMEOUT')

# CHROMEDRIVER
LOCAL_USE = config['CHROMEDRIVER'].getboolean('LOCAL_USE')
HUB_ADDRESS = config['CHROMEDRIVER']['HUB_ADDRESS']


# Validaciones:
if not USERNAME or not PASSWORD:
    raise ValueError('Las credenciales de usuario no están configuradas correctamente.')

if not SCHEDULE_ID:
    raise ValueError('El ID de programación no está configurado.')

if not PERIOD_START or not PERIOD_END:
    raise ValueError('El período objetivo no está configurado correctamente.')

if len(YOUR_EMBASSIES) == 0:
    raise ValueError('Please enter at least 1 embassy in the config.')

if not validate_embassies(YOUR_EMBASSIES):
    raise ValueError('All embassies must have the same EMBASSY value.')


if not SENDGRID_API_KEY or not SENDGRID_EMAIL_SENDER or not SENDGRID_TARGET_EMAIL:
    log.error('Email notifications disabled. Please provide your SendGrid credentials.')

if not PUSHOVER_TOKEN or not PUSHOVER_USER:
    log.error('Pushover notifications disabled. Please provide your Pueshover credentials.')

# Puedes agregar más validaciones según sea necesario.


