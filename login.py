from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from datetime import datetime
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
import os

username = "E0584"
password = ""

service = Service(executable_path=ChromeDriverManager().install())
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

def login(driver, username, password):
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--remote-allow-origins=*")
    driver.get("https://navyacarehrm.greythr.com/")
    driver.maximize_window()
    time.sleep(2)
    usr = driver.find_element(By.ID, "username")
    usr.send_keys(username)
    pw = driver.find_element(By.ID, "password")
    pw.send_keys(password)
    element = driver.find_element(By.XPATH, "//button[@type='submit']")
    element.click()
    time.sleep(8)


def signin(driver, mode_of_work):
    """
    Sign in the user with the specified mode of work: 'work from home' or 'work from office'.
    """
    login(driver, username, password) 
    
    driver.find_element(By.XPATH, "//gt-button[@shade='primary']").click()
    time.sleep(2) 
    
    select = driver.find_element(By.TAG_NAME, "gt-dropdown")
    select.click()
    time.sleep(1)
    
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", select)
    dropdown_items = shadow_root.find_elements(By.CSS_SELECTOR, ".dropdown-item .item-label")
    
    valid_modes = {"work from home", "work from office."}
    mode_of_work = mode_of_work.strip().lower()
    
    if mode_of_work not in valid_modes:
        return f"Unable to sign in. Invalid mode of work: '{mode_of_work}'"
    
    for item in dropdown_items:
        if item.text.strip().lower() == mode_of_work:
            item.click()
            print(f"Clicked on '{mode_of_work.capitalize()}'")
            time.sleep(2)
            break
    else:
        return f"Unable to sign in. '{mode_of_work.capitalize()}' option not found."
    
    signin_button_parent = driver.find_element(By.XPATH, "//gt-button[@shade='primary']")
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", signin_button_parent)
    signin_button = shadow_root.find_element(By.XPATH, ".//button[contains(@class, 'btn') and normalize-space(text())='Sign In']")
    
    
    time.sleep(2)
    signin_button.click()
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Successfully signed in to '{mode_of_work.capitalize()}' at {current_time}"



output_text = signin(driver, mode_of_work="work from office.")
print(output_text)



# def main():

#     today = datetime.now().strftime('%A')  # Gives full day name like 'Monday'

#     # Check and execute based on the day
#     if today in ['Monday', 'Tuesday', 'Wednesday']:
#         function_a()
#     elif today in ['Thursday', 'Friday']:
#         function_b()
#     else:
#         print("It's Saturday or Sunday. Doing nothing.")
