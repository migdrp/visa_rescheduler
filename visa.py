import time
import random
import sys
import traceback

from utils.logger import Logger
from datetime import datetime

from config.config_validation import USERNAME, PASSWORD, RETRY_TIME_L_BOUND, RETRY_TIME_U_BOUND, WORK_LIMIT_TIME, WORK_COOLDOWN_TIME, BAN_COOLDOWN_TIME, YOUR_EMBASSIES,SCHEDULE_ID

from handlers.notification_handler import send_notification
from handlers.selenium_handler import start_driver, login_to_site, get_embassy_dates, get_available_date, reschedule
from utils.visa_utils import info_logger, get_logout_url


log = Logger('VISA RESCHEDULER')

# Time Section:
minute = 60
hour = 60 * minute

print('Welcome to Visa Rescheduler. Starting selenium driver...')
driver = start_driver()
log.debug('Reading your embassies...')
embassies = YOUR_EMBASSIES
log.debug('Embassies: ', YOUR_EMBASSIES)



if __name__ == "__main__":
    is_first_iteration = True
    embassy_to_use = YOUR_EMBASSIES[0]  # Use only the first embassy for now
    log.debug(f"Using embassy: {embassy_to_use}")
    URL_LOGOUT = get_logout_url(embassy_to_use, SCHEDULE_ID)
    
    while True:
        log_file_name = "log_" + str(datetime.now().date()) + ".txt"
        
        if is_first_iteration:
            start_time = time.time()
            elapsed_time = 0
            request_count = 0
            login_to_site(driver, USERNAME, PASSWORD, embassy_to_use)
            is_first_iteration = False
        
        request_count += 1
        log_message = "-" * 60 + f"\nRequest count: {request_count}, Log time: {datetime.today()}\n"
        log.debug(log_message)
        
        try:
            available_dates = get_embassy_dates(driver, embassy_to_use)
            
            if not available_dates:
                log_message = f"List is empty, probably banned!\n\tSleeping for {BAN_COOLDOWN_TIME} hours!\n"
                log.debug(log_message)
                send_notification("BAN", log_message)
                driver.get(URL_LOGOUT)
                time.sleep(BAN_COOLDOWN_TIME * hour)
                is_first_iteration = True
            else:
                log.debug("Available dates: ", available_dates)
                
                selected_date = get_available_date(available_dates)
                
                if selected_date:
                    notification_title, log_message = reschedule(selected_date)
                    break
                
                retry_wait_time = random.randint(RETRY_TIME_L_BOUND, RETRY_TIME_U_BOUND)
                elapsed_time = time.time() - start_time
                log_message = f"Working Time:  ~ {elapsed_time/minute:.2f} minutes"
                log.debug(log_message)
                
                if elapsed_time > WORK_LIMIT_TIME * hour:
                    log_message = f"Break-time after {WORK_LIMIT_TIME} hours | Repeated {request_count} times"
                    send_notification("REST", log_message)
                    driver.get(URL_LOGOUT)
                    time.sleep(WORK_COOLDOWN_TIME * hour)
                    is_first_iteration = True
                else:
                    log_message = f"Retry Wait Time: {retry_wait_time} seconds"
                    log.debug(log_message)
                    time.sleep(retry_wait_time)
        except Exception as e:
            log_message = f"Exception occurred: {str(e)}"
            log.debug(log_message)
            traceback.print_exception(*sys.exc_info())
            notification_title = "EXCEPTION"
            break


log.debug(log_message)
send_notification(notification_title, log_message)
driver.get(URL_LOGOUT)
driver.stop_client()
driver.quit()



"""

if __name__ == "__main__":
    first_loop = True
    while 1:
        LOG_FILE_NAME = "log_" + str(datetime.now().date()) + ".txt"
        if first_loop:
            t0 = time.time()
            total_time = 0
            Req_count = 0
            login_to_site(driver, USERNAME, PASSWORD)
            first_loop = False
        Req_count += 1
        try:
            msg = "-" * 60 + f"\nRequest count: {Req_count}, Log time: {datetime.today()}\n"
            print(msg)
            info_logger(LOG_FILE_NAME, msg)
            dates = get_date()
            if not dates:
                # Ban Situation
                msg = f"List is empty, Probabely banned!\n\tSleep for {BAN_COOLDOWN_TIME} hours!\n"
                print(msg)
                info_logger(LOG_FILE_NAME, msg)
                send_notification("BAN", msg)
                driver.get(SIGN_OUT_LINK)
                time.sleep(BAN_COOLDOWN_TIME * hour)
                first_loop = True
            else:
                # Print Available dates:
                msg = ""
                for d in dates:
                    msg = msg + "%s" % (d.get('date')) + ", "
                msg = "Available dates:\n"+ msg
                print(msg)
                info_logger(LOG_FILE_NAME, msg)
                date = get_available_date(dates)
                if date:
                    # A good date to schedule for
                    END_MSG_TITLE, msg = reschedule(date)
                    break
                RETRY_WAIT_TIME = random.randint(RETRY_TIME_L_BOUND, RETRY_TIME_U_BOUND)
                t1 = time.time()
                total_time = t1 - t0
                msg = "\nWorking Time:  ~ {:.2f} minutes".format(total_time/minute)
                print(msg)
                info_logger(LOG_FILE_NAME, msg)
                if total_time > WORK_LIMIT_TIME * hour:
                    # Let program rest a little
                    send_notification("REST", f"Break-time after {WORK_LIMIT_TIME} hours | Repeated {Req_count} times")
                    driver.get(SIGN_OUT_LINK)
                    time.sleep(WORK_COOLDOWN_TIME * hour)
                    first_loop = True
                else:
                    msg = "Retry Wait Time: "+ str(RETRY_WAIT_TIME)+ " seconds"
                    print(msg)
                    info_logger(LOG_FILE_NAME, msg)
                    time.sleep(RETRY_WAIT_TIME)
        except Exception as ex:
            # Exception Occured
            errorMessage = ex.__str__()
            exc_info = sys.exc_info()
            print('Error: ',  errorMessage)
            traceback.print_exception(*exc_info)
            msg = f"Break the loop after exception!\n"
            END_MSG_TITLE = "EXCEPTION"
            break

print(msg)
info_logger(LOG_FILE_NAME, msg)
send_notification(END_MSG_TITLE, msg)
driver.get(SIGN_OUT_LINK)
driver.stop_client()
driver.quit()
"""