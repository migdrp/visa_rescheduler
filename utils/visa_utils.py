
from datetime import datetime
from utils.logger import Logger
from utils.embassy import Embassies


log = Logger('VISA UTILS')  


def get_embassy_vars(emb:str):
  return dict(  
    EMBASSY = Embassies[emb][0],
    FACILITY_ID = Embassies[emb][1],
    REGEX_CONTINUE_BTN_TEXT = Embassies[emb][2]
  )



def get_login_url(emb:str): 
  VARS= get_embassy_vars(emb)
  URL_LOGIN = f"https://ais.usvisa-info.com/{VARS['EMBASSY']}/niv/users/sign_in"
  return URL_LOGIN



def get_appointment_url(emb:str, SCHEDULE_ID:str): 
  VARS= get_embassy_vars(emb)
  URL_APPOINTMENT = f"https://ais.usvisa-info.com/{VARS['EMBASSY']}/niv/schedule/{SCHEDULE_ID}/appointment"
  return URL_APPOINTMENT

def get_dates_url(emb:str, SCHEDULE_ID:str):
  VARS= get_embassy_vars(emb)
  URL_DATES = f"https://ais.usvisa-info.com/{VARS['EMBASSY']}/niv/schedule/{SCHEDULE_ID}/appointment/days/{VARS['FACILITY_ID']}.json?appointments[expedite]=false"
  return URL_DATES

def get_times_url(emb:str, date:str, SCHEDULE_ID:str):
  VARS= get_embassy_vars(emb)
  URL_TIMES = f"https://ais.usvisa-info.com/{VARS['EMBASSY']}/niv/schedule/{SCHEDULE_ID}/appointment/times/{VARS['FACILITY_ID']}.json?date={date}&appointments[expedite]=false"
  return URL_TIMES

def get_logout_url(emb:str, SCHEDULE_ID:str):
  VARS= get_embassy_vars(emb)
  URL_LOGOUT = f"https://ais.usvisa-info.com/{VARS['EMBASSY']}/niv/users/sign_out"
  return URL_LOGOUT


def validate_embassies(embassies:list):
  """
    Verifies that all the YOUR_EMBASSIES have the same EMBASSY param in the embbasy.py
    It must be validated because the URLS must be in the same embassy that logins.
  """
  embassy_values = [get_embassy_vars(emb)['EMBASSY'] for emb in embassies]
  if len(set(embassy_values)) != 1:
    log.debug('All embassies must have the same EMBASSY value.')
    return False
    
  return True


def info_logger(file_path, log):
    # file_path: e.g. "log.txt"
    with open(file_path, "a") as file:
        file.write(str(datetime.now().time()) + ":\n" + log + "\n")