from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import pytz
import time
import random

USERS = {
    "user1": {
        "username": "E0584",
        "password": os.getenv('GREYT_PASSWORD_USER1'),
        "email": "riddhimann@navyatech.in",
        "holiday_list": ["07.07.2025", "15.08.2025", "27.08.2025", "01.10.2025", "02.10.2025", "20.10.2025", "25.12.2025"]
    },
    "user2": {
        "username": "E0614",
        "password": os.getenv('GREYT_PASSWORD_USER2'),
        "email": "kirana@navyatech.in",
        "holiday_list": ["31.03.2025", "01.04.2025", "02.04.2025", "18.04.2025", "01.05.2025", "09.05.2025", "06.07.2025", "15.08.2025", "27.08.2025", "01.10.2025", "02.10.2025", "20.10.2025", "25.12.2025"]
    }
}

# Chrome setup
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

service = Service(ChromeDriverManager().install())

# This is a test to push code changes to feature branch

def login(driver, username, password):
    try:
        driver.get("https://navyacarehrm.greythr.com/")
        print("Opened login page.")

        usr = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "username")))
        usr.send_keys(username)

        pw = driver.find_element(By.ID, "password")
        pw.send_keys(password)

        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_btn.click()

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "gt-button")))
        print("Logged in successfully!")
    except Exception as e:
        print(f"Failed to log in! Error: {e}")

def signin(driver, username, password, mode_of_work):
    login(driver, username, password)
    try:
        sign_in_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//gt-button[@shade='primary']"))
        )
        sign_in_button.click()
        print("Clicked sign-in button.")

        select = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "gt-dropdown")))
        select.click()
        time.sleep(3)

        shadow_root = driver.execute_script("return arguments[0].shadowRoot", select)
        dropdown_items = shadow_root.find_elements(By.CSS_SELECTOR, ".dropdown-item .item-label")

        for item in dropdown_items:
            if item.text.strip().lower() == mode_of_work:
                item.click()
                print(f"Selected '{mode_of_work}'")
                break
        else:
            return f"Option '{mode_of_work}' not found."

        time.sleep(3)
        
        shadow_host = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".flex.justify-end.hydrated"))
        )
        signin_shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        signin_button = signin_shadow_root.find_element(By.CSS_SELECTOR, ".btn.btn-primary.btn-medium")
        
        if signin_button:
            # random_time = random.randint(120,300)
            # print(f"Sleeping for {random_time} seconds...")
            # time.sleep(random_time)
            signin_button.click()
            print("Signin button clicked.")
        else:
            return "Signin button not found."

        ist_timezone = pytz.timezone('Asia/Kolkata')
        current_time_ist = datetime.now(ist_timezone).strftime("%Y-%m-%d %H:%M:%S")
        # return f"Punch successful: '{mode_of_work}' at {current_time_ist}, added randomized sleep for {random_time} seconds."
        return f"Punch successful: '{mode_of_work}' at {current_time_ist}"
    except Exception as e:
        return f"Signin failed! Error: {e}"

def send_email(email, subject, body):
    sender_email = "riddhimann@navyatech.in"
    password = os.getenv('APP_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def process_user(user_config):
    driver = webdriver.Chrome(service=service, options=chrome_options)
    ist_timezone = pytz.timezone("Asia/Kolkata")
    current_datetime = datetime.now(ist_timezone)
    current_day = current_datetime.strftime("%A").lower()
    current_date = current_datetime.strftime("%d.%m.%Y")

    if current_date in user_config["holiday_list"]:
        holiday_message = f"Today, ({current_date}) is a holiday. No punch required."
        print(holiday_message)
        send_email(user_config["email"], "Punch Report - Holiday Notice", holiday_message)
        driver.quit()
        return

    work_mode = "work from home" if current_day in ['monday', 'tuesday', 'wednesday'] else "work from office."
    signin_message = f"Triggering punch for {user_config['username']} with mode: '{work_mode}' - {current_day}"
    print(signin_message)
    output = signin(driver, user_config["username"], user_config["password"], work_mode)
    
    print(output)
    send_email(user_config["email"], "Punch Report", signin_message + "\n" + output)
    driver.quit()

def main():
    for user, config in USERS.items():
        process_user(config)

if __name__ == "__main__":
    main()
