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

# Fixed holiday list
HOLIDAY_LIST = ["20.02.2025", "21.02.2025", "14.03.2025", "21.03.2025", "31.03.2025", "18.04.2025",
                "01.05.2025", "06.07.2025", "15.08.2025", "27.08.2025", "01.10.2025", "02.10.2025",
                "20.10.2025", "25.12.2025"]

USERNAME = "E0584"
PASSWORD = os.getenv('GREYT_PASSWORD')

# Chrome setup
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def login(driver, username, password):
    """Logs into the GreyHR system."""
    try:
        driver.get("https://navyacarehrm.greythr.com/")
        print("Opened login page.")

        # Wait for username field
        usr = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "username")))
        usr.send_keys(username)

        pw = driver.find_element(By.ID, "password")
        pw.send_keys(password)

        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_btn.click()

        # Wait until login is successful
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "gt-button")))
        print("Logged in successfully!")

    except Exception as e:
        print(f"Failed to log in! Error: {e}")

def signin(driver, mode_of_work):
    """Performs punch-in for the given mode of work."""
    login(driver, USERNAME, PASSWORD)

    try:
        # Wait for button and click
        sign_in_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//gt-button[@shade='primary']"))
        )
        sign_in_button.click()
        print("Clicked sign-in button.")

        # Wait for dropdown to appear
        select = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "gt-dropdown")))
        select.click()
        time.sleep(3)

        # Extract shadow root
        shadow_root = driver.execute_script("return arguments[0].shadowRoot", select)
        dropdown_items = shadow_root.find_elements(By.CSS_SELECTOR, ".dropdown-item .item-label")

        valid_modes = {"work from home", "work from office."}
        mode_of_work = mode_of_work.strip().lower()

        if mode_of_work not in valid_modes:
            return f"Invalid mode of work: '{mode_of_work}'"

        # Select correct mode
        for item in dropdown_items:
            if item.text.strip().lower() == mode_of_work:
                item.click()
                print(f"Selected '{mode_of_work}'")
                break
        else:
            return f"Option '{mode_of_work}' not found."

        time.sleep(3)

        # Find and click Sign-in button inside shadow DOM
        shadow_host = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".flex.justify-end.hydrated"))
        )
        signin_shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
        signin_button = signin_shadow_root.find_element(By.CSS_SELECTOR, ".btn.btn-primary.btn-medium")

        if signin_button:
            signin_button.click()
            print("Signin button clicked.")
        else:
            return "Signin button not found."

        # Get current timestamp
        utc_time = datetime.now(pytz.utc)
        ist_timezone = pytz.timezone('Asia/Kolkata')
        current_time_ist = utc_time.astimezone(ist_timezone).strftime("%Y-%m-%d %H:%M:%S")

        return f"Punch successful: '{mode_of_work}' at {current_time_ist}"

    except Exception as e:
        return f"Signin failed! Error: {e}"

def send_email(subject, body):
    """Sends an email with the provided subject and body."""
    sender_email = "riddhimann@navyatech.in"
    receiver_email = "riddhimann@navyatech.in"
    password = os.getenv('APP_PASSWORD')

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def main(driver):
    """Main function that checks for holidays and triggers punch-in."""
    ist_timezone = pytz.timezone("Asia/Kolkata")
    current_datetime = datetime.now(ist_timezone)
    current_day = current_datetime.strftime("%A").lower()
    current_date = current_datetime.strftime("%d.%m.%Y")

    print(f"Executing script on {current_date}, {current_day}")

    if current_date in HOLIDAY_LIST:
        holiday_message = f"Today, ({current_date}) is a holiday. No punch required."
        print(holiday_message)
        send_email("Punch Report - Holiday Notice", holiday_message)
        return

    work_mode = "work from home" if current_day in ['monday', 'tuesday', 'wednesday'] else "work from office."

    signin_message = f"Triggering punch with mode: '{work_mode}' - {current_day}"
    print(signin_message)
    output = signin(driver, work_mode)

    print(output)
    send_email("Punch Report", signin_message + "\n" + output)

main(driver)
