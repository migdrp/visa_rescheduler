# Archivo: selenium_handler.py
# Carpeta: /handlers

import time
import json
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from config.config_validation import LOCAL_USE, HUB_ADDRESS


if LOCAL_USE:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
else:
    driver = webdriver.Remote(command_executor=HUB_ADDRESS, options=webdriver.ChromeOptions())

    

def auto_action(label, find_by, el_type, action, value, sleep_time=0):
    print('\t' + label + ':', end='')
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
    print('\t\tCheck!')
    if sleep_time:
        time.sleep(sleep_time)

def start_driver():
    if LOCAL_USE:
        driver = webdriver.Chrome(ChromeDriverManager().install())
    else:
        driver = webdriver.Remote(
            command_executor=HUB_ADDRESS,
            desired_capabilities={'browserName': 'chrome', 'javascriptEnabled': True}
        )
    return driver

def login_to_site(driver, username, password):
    driver.get('URL_DEL_SITIO')  # Reemplaza con la URL del sitio de login
    auto_action('Ingresando usuario', 'id', 'input_username', 'send', username, 1)
    auto_action('Ingresando contraseña', 'id', 'input_password', 'send', password, 1)
    auto_action('Click en botón de inicio', 'id', 'login_button', 'click', '', 2)

def navigate_to_schedule_page(driver):
    auto_action('Navegando a programación', 'id', 'schedule_nav', 'click', '', 2)

def check_available_slots(driver):
    slots = driver.find_elements(By.XPATH, 'XPATH_DE_LOS_SLOTS')  # Reemplaza con el XPath correcto
    available_slots = [slot for slot in slots if 'disponible' in slot.text.lower()]
    return available_slots

def reschedule_appointment(driver):
    auto_action('Click en reprogramar', 'id', 'reschedule_button', 'click', '', 2)
    # Aquí puedes agregar más acciones para completar el proceso de reprogramación

def another_selenium_function(driver):
    # Ejemplo de otra función
    pass

def yet_another_selenium_function(driver):
    # Ejemplo de otra función
    pass