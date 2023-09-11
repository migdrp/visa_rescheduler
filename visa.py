import time
import random
import sys
import traceback
import os


from urllib3.exceptions import ProtocolError
from selenium.common.exceptions import WebDriverException

from utils.logger import Logger
from datetime import datetime

from config.config_validation import USERNAME, PASSWORD, RETRY_TIME_L_BOUND, RETRY_TIME_U_BOUND, WORK_LIMIT_TIME, WORK_COOLDOWN_TIME, BAN_COOLDOWN_TIME, YOUR_EMBASSIES,SCHEDULE_ID, STEP_TIME, REQUEST_DATES_TIME

from handlers.notification_handler import send_notification, send_pushover, send_email
from handlers.selenium_handler import start_driver, login_to_site, get_embassy_dates, get_available_date, reschedule, SeleniumTimeoutException
from utils.visa_utils import info_logger, get_logout_url, validate_embassies


log = Logger('VISA RESCHEDULER')

# Time Section:
minute = 60
hour = 60 * minute






    
def run_program(embassies:list, state:str):

    if not validate_embassies(embassies): 
        raise ValueError('Not valid multiple embassies, all embassies must share the same login site')

    reschedule_start_time = time.time()
    reschedule_elapsed_time = 0
    reschedule_try_count = 0
    reschedule_login_embassy = embassies[0]

    if state == 'LOGGED_OUT':
        login_to_site(driver, USERNAME, PASSWORD, reschedule_login_embassy)
        state = 'LOGGED_IN'


    if state == 'LOGGED_IN':
        reschedule_try_count += 1
        log.debug(f"Reschedule try count: {reschedule_try_count}, Log time: {datetime.today()}")

        for idx, emb in enumerate(embassies):

            log.debug(f"Checking {emb} embassy dates.")
            emb_available_dates = get_embassy_dates(driver, emb)

            if not emb_available_dates and idx < len(embassies) - 1:
                log.debug(f"Embassy {emb} without dates, checking another one!")
                time.sleep(REQUEST_DATES_TIME)
                continue

            elif not emb_available_dates and idx == len(embassies) - 1:
                log_message = f"All embassies dates are empty, probably not enabled yet on your embsassies!  Sleeping for {BAN_COOLDOWN_TIME} hours!"
                log.debug(log_message)
                send_notification("ALL EMBASSIES WITHOUT DATES", log_message)
                driver.get(URL_LOGOUT)
                time.sleep(BAN_COOLDOWN_TIME * hour)
                state = 'LOGGED_OUT'
                break

            
            elif emb_available_dates and idx < len(embassies) - 1: 
                log.debug(f"Embassy {emb} with available dates: ", emb_available_dates)
                selected_date = get_available_date(emb_available_dates)

                if selected_date:
                    
                    log.debug(f"GOT DATE!! Embassy {emb} with available date between desired range, trying to reschedule: ", selected_date)
                    notification_title, log_message = reschedule(driver, emb, selected_date)
                    send_notification(notification_title, log_message)
                    log.debug(log_message)
                    driver.get(URL_LOGOUT)
                    driver.stop_client()
                    driver.quit()
                    state = 'LOGGED_OUT'
                    time.sleep(REQUEST_DATES_TIME)
                    break

                else:
                    log.debug(f"Embassy {emb} without available date between desired range, trying another embassy ", selected_date)
                    time.sleep(REQUEST_DATES_TIME)
                    continue
            
            elif emb_available_dates and idx == len(embassies) - 1: 
                log.debug(f"Embassy {emb} with available dates: ", emb_available_dates)
                selected_date = get_available_date(emb_available_dates)

                if selected_date:
                    
                    log.debug(f"GOT DATE!! Embassy {emb} with available date between desired range, trying to reschedule: ", selected_date)
                    notification_title, log_message = reschedule(driver, emb, selected_date)

                    if notification_title == "RESCHEDULE SUCCESS":


                        send_notification(notification_title, log_message)
                        log.debug(log_message)
                        driver.get(URL_LOGOUT)
                        driver.stop_client()
                        driver.quit()
                        state = 'LOGGED_OUT'
                        break
                        
                    elif notification_title == "RESCHEDULE FAIL":
                        log_message = f"Reschedule fail, retry Wait Time: {REQUEST_DATES_TIME} seconds"
                        log.debug(log_message)
                        time.sleep(REQUEST_DATES_TIME)
                        break
                
                else:

                    retry_wait_time = random.randint(RETRY_TIME_L_BOUND, RETRY_TIME_U_BOUND)
                    reschedule_elapsed_time = time.time() - reschedule_start_time
                    log.debug(f"Working Time:  ~ {reschedule_elapsed_time/minute:.2f} minutes")

                    if reschedule_elapsed_time > WORK_LIMIT_TIME * hour:
                        log_message =f"Break-time after {WORK_LIMIT_TIME} hours | Repeated {reschedule_try_count} times, no dates found"
                        log.debug(log_message)
                        send_notification("REST", log_message)
                        driver.get(URL_LOGOUT)
                        time.sleep(WORK_COOLDOWN_TIME * hour)
                        state = 'LOGGED_OUT'
                        break
                    else:
                        log_message = f"Retry Wait Time: {retry_wait_time} seconds"
                        log.debug(log_message)
                        time.sleep(retry_wait_time)
                        

            else:
                log_message = f"Retry Wait Time: {retry_wait_time} seconds"
                log.debug(log_message)
                time.sleep(retry_wait_time)
                

       

if __name__ == "__main__":
    log.debug('Welcome to Visa Rescheduler. Starting selenium driver...')
    driver = start_driver()
    log.debug('Reading your embassies...')
    embassies = YOUR_EMBASSIES
    log.debug('Embassies: ', YOUR_EMBASSIES)
    URL_LOGOUT = get_logout_url(YOUR_EMBASSIES[0], SCHEDULE_ID)
    state = 'LOGGED_OUT'
    while True:
        try:
            run_program(embassies, state)

        except SeleniumTimeoutException as ste:
            error_message = f"Selenium Error encountered: {str(ste)}"
            send_notification("SELENIUM TIMEOUT ERROR", error_message)
            log.debug(error_message)
            os.system("taskkill /f /im chromedriver.exe /T")
            time.sleep(3)
            driver = start_driver()

        except ProtocolError:
            log.debug("Connection was reset after forcibly closing the driver.")
            time.sleep(3)
            driver = start_driver()

        except WebDriverException:
            log.debug("Connection was reset after forcibly closing the driver.")
            time.sleep(3)
            driver = start_driver()


        except ConnectionResetError:
            log.debug("Connection was reset after forcibly closing the driver.")
            time.sleep(3)
            driver = start_driver()

        except Exception as e:
            error_message = f"Error encountered: {str(e)}"
            log.debug(error_message)
            send_notification("ERROR", error_message)
            driver.get(URL_LOGOUT)
            driver.stop_client()
            driver.quit()
            driver = start_driver()
        
        