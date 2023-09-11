import time
import json
import requests
import threading

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options



from config.config_validation import LOCAL_USE, HUB_ADDRESS, STEP_TIME, SELENIUM_TIMEOUT, PERIOD_END, PERIOD_START, SCHEDULE_ID
from utils.visa_utils import get_login_url, get_appointment_url, get_dates_url, get_times_url, get_logout_url, get_embassy_vars
from utils.logger import Logger

log = Logger('SELENIUM HANDLER')  


JS_SCRIPT = ("var req = new XMLHttpRequest();"
    f"req.open('GET', '%s', false);"
    "req.setRequestHeader('Accept', 'application/json, text/javascript, */*; q=0.01');"
    "req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');"
    f"req.setRequestHeader('Cookie', '_yatri_session=%s');"
    "req.send(null);"
    "return req.responseText;")




def auto_action(driver, label, find_by, el_type, action, value, sleep_time=0):
    """
    Do and automate the selenium actions, interacts with the elements on the browser.
    """
    log.debug('Todo action: ', label)
    # Find Element By
    if find_by.lower() == 'id':
        item = driver.find_element(By.ID, el_type)
    elif find_by.lower() == 'name':
        item = driver.find_element(By.NAME, el_type)
    elif find_by.lower() == 'class':
        item = driver.find_element(By.CLASS_NAME, el_type)
    elif find_by.lower() == 'xpath':
        item = driver.find_element(By.XPATH, el_type)
    else:
        return 0
    # Do Action:
    if action.lower() == 'send':
        item.send_keys(value)
    elif action.lower() == 'click':
        item.click()
    else:
        return 0
    log.debug('Action completed ✔️')
    if sleep_time:
        time.sleep(sleep_time)
        

def start_driver():
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'

    if not LOCAL_USE and not HUB_ADDRESS:
        log.debug('Selenium Hub Address not provided, forced Local')

    if LOCAL_USE:


        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    elif not LOCAL_USE and HUB_ADDRESS:
        driver = webdriver.Remote(command_executor=HUB_ADDRESS, options=chrome_options)
    else:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def login_to_site(driver, username:str, password:str, emb:str):
    URL_LOGIN = get_login_url(emb)
    REGEX_CONTINUE_BTN_TEXT = get_embassy_vars(emb)['REGEX_CONTINUE_BTN_TEXT']
    log.debug('Going to login URL')
    #driver.get(URL_LOGIN)
    get_with_timeout(driver, URL_LOGIN, SELENIUM_TIMEOUT)  # Setting a 30 seconds timeout

    log.debug('login URL got')
    time.sleep(STEP_TIME)
    Wait(driver, SELENIUM_TIMEOUT).until(EC.presence_of_element_located((By.NAME, "commit")))
    log.debug('Wait completed')
    auto_action(driver, "Click bounce", "xpath", '//a[@class="down-arrow bounce"]', "click", "", STEP_TIME)
    auto_action(driver, "Entering email", "id", "user_email", "send", username, STEP_TIME)
    auto_action(driver, "Entering password", "id", "user_password", "send", password, STEP_TIME)
    auto_action(driver, "Clicking privacy checkbox", "class", "icheckbox", "click", "", STEP_TIME)
    auto_action(driver, "Clicking login", "name", "commit", "click", "", STEP_TIME)
    Wait(driver, SELENIUM_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '" + REGEX_CONTINUE_BTN_TEXT + "')]")))

def get_embassy_dates(driver, emb:str):
    URL_DATES = get_dates_url(emb, SCHEDULE_ID)
    session = driver.get_cookie("_yatri_session")["value"]
    script = JS_SCRIPT % (str(URL_DATES), session)
    content = driver.execute_script(script)
    dates= json.loads(content)
    log.debug(f'Got {emb} dates:',dates)
    return dates

def get_embasy_date_times(driver, emb:str, date):
    
    URL_TIMES = get_times_url(emb, date, SCHEDULE_ID)
    session = driver.get_cookie("_yatri_session")["value"]
    script = JS_SCRIPT % (str(URL_TIMES), session)
    content = driver.execute_script(script)
    data = json.loads(content)
    times = data.get("available_times")[-1]
    log.debug(f"Got {emb} date {date} time successfully:", times)
    return time



def get_available_date(dates):
    # Evaluation of different available dates
    def is_in_period(date, PSD, PED):
        new_date = datetime.strptime(date, "%Y-%m-%d")
        result = ( PED > new_date and new_date > PSD )
        # print(f'{new_date.date()} : {result}', end=", ")
        return result
    
    PED = datetime.strptime(PERIOD_END, "%Y-%m-%d")
    PSD = datetime.strptime(PERIOD_START, "%Y-%m-%d")
    for d in dates:
        date = d.get('date')
        if is_in_period(date, PSD, PED):
            return date
    log.debug(f"No available dates between ({PSD.date()}) and ({PED.date()})!")
    return None


def reschedule(driver, emb:str, date:str):
    time = get_embasy_date_times(driver, emb, date)

    URL_APPOINTMENT = get_appointment_url(emb, SCHEDULE_ID)
    FACILITY_ID = get_embassy_vars(emb)['FACILITY_ID']
    driver.get(URL_APPOINTMENT)

    headers = {
        "User-Agent": driver.execute_script("return navigator.userAgent;"),
        "Referer": URL_APPOINTMENT,
        "Cookie": "_yatri_session=" + driver.get_cookie("_yatri_session")["value"]
    }

    data = {
        "utf8": driver.find_element(by=By.NAME, value='utf8').get_attribute('value'),
        "authenticity_token": driver.find_element(by=By.NAME, value='authenticity_token').get_attribute('value'),
        "confirmed_limit_message": driver.find_element(by=By.NAME, value='confirmed_limit_message').get_attribute('value'),
        "use_consulate_appointment_capacity": driver.find_element(by=By.NAME, value='use_consulate_appointment_capacity').get_attribute('value'),
        "appointments[consulate_appointment][facility_id]": FACILITY_ID,
        "appointments[consulate_appointment][date]": date,
        "appointments[consulate_appointment][time]": time,
    }
    r = requests.post(URL_APPOINTMENT, headers=headers, data=data)
    
    log.debug(f'Reschedule response: {r.status_code}, content: {r.content}')

    if(r.text.find('Successfully Scheduled') != -1):
        title = "SUCCESS"
        msg = f"Rescheduled Successfully! {date} {time}"
    else:
        title = "FAIL"
        msg = f"Reschedule Failed!!! {date} {time}"
    return [title, msg]


def is_logged_in(driver):
    content = driver.page_source
    if(content.find("error") != -1):
        return False
    return True



def get_with_timeout(driver, url, timeout):
    event = threading.Event()
    def worker():
        driver.get(url)
        event.set()
    thread = threading.Thread(target=worker)
    thread.start()
    event.wait(timeout)
    if not event.is_set():
        raise SeleniumTimeoutException(f"Timed out after {timeout} seconds while loading {url}")
    


class SeleniumTimeoutException(Exception):
    pass