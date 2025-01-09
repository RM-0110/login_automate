from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import pytz
import time 

holiday_list = ["01.01.2025", "14.01.2025", "14.03.2025", "21.03.2025", "31.03.2025", "18.04.2025", "01.05.2025", "06.07.2025", "15.08.2025", "27.08.2025", "01.10.2025", "02.10.2025", "20.10.2025", "25.12.2025"]

username = "E0584"
password = os.getenv('GREYT_PASSWORD')

service = Service(executable_path=ChromeDriverManager().install())
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=service, options=options)

def login(driver, username, password):
    try:
        driver.get("https://navyacarehrm.greythr.com/")
        driver.maximize_window()
        
        # Wait until the username field is visible
        usr = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "username")))
        usr.send_keys(username)
        
        pw = driver.find_element(By.ID, "password")
        pw.send_keys(password)
        
        element = driver.find_element(By.XPATH, "//button[@type='submit']")
        element.click()

        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//gt-button[@shade='primary']")))
        print("Logged in successfully!")
    except Exception as e:
        print("Failed to log in! Error: %s" % e)


def signin(driver, mode_of_work):

    login(driver, username, password) 
    
    # Wait for the button and click it
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//gt-button[@shade='primary']"))).click()
    
    # Wait for the dropdown to appear
    select = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "gt-dropdown")))
    select.click()

    time.sleep(10)
    
    # Wait for shadow DOM to load
    shadow_root = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "gt-dropdown"))
    )
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", select)
    dropdown_items = shadow_root.find_elements(By.CSS_SELECTOR, ".dropdown-item .item-label")
    
    valid_modes = {"work from home", "work from office."}
    mode_of_work = mode_of_work.strip().lower()
    
    if mode_of_work not in valid_modes:
        return f"Unable to sign in. Invalid mode of work: '{mode_of_work}'"
    
    for item in dropdown_items:
        if item.text.strip().lower() == mode_of_work:
            item.click()
            print(f"Clicked on '{mode_of_work}'")
            break
    else:
        return f"Unable to sign in. '{mode_of_work}' option not found."

    time.sleep(5)
    
    shadow_host = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".flex.justify-end.hydrated"))
    )
    signin_shadow_root  = shadow_host.shadow_root
    signin_button = signin_shadow_root.find_element(By.CSS_SELECTOR, ".btn.btn-primary.btn-medium")
    time.sleep(2)
    signin_button.click()
    print("Signin button clicked.")

    utc_time = datetime.now(pytz.utc)
    ist_timezone = pytz.timezone('Asia/Kolkata')
    current_time_ist = utc_time.astimezone(ist_timezone).strftime("%Y-%m-%d %H:%M:%S")
    return f"Successful punch done on '{mode_of_work}' at {current_time_ist}"


def send_email(subject, body):
    # Set up email credentials and server
    sender_email = "riddhimann@navyatech.in"  # Your email address
    receiver_email = "riddhimann@navyatech.in"  # Receiver email address (it can be the same as sender)
    password = os.getenv('APP_PASSWORD')  # Get password from environment variables

    # Set up the MIME structure for the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish connection to Gmail SMTP server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, password)  # Log in using the email credentials
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)  # Send email
        server.quit()  # Close the connection
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")


def main(driver):
    # Define IST timezone
    ist_timezone = pytz.timezone("Asia/Kolkata")
    
    # Get the current date and day in IST
    current_datetime = datetime.now(ist_timezone)
    current_day = current_datetime.strftime("%A").lower()  # Get the current day of the week
    current_date = current_datetime.strftime("%d.%m.%Y")  # Get the current date in the format dd.mm.yyyy

    print("Executing script on " + str(current_date + ", " + str(current_day)))
    
    # Check if today is a holiday
    if current_date in holiday_list:
        holiday_message = f"Today, ({current_date}) is a holiday. No sign-in or sign-out will be performed."
        print(holiday_message)
        send_email("Punch Report - Holiday Notice", holiday_message)
        return

    if current_day in ['monday', 'tuesday', 'wednesday']:
        mode_of_work = "work from home"
        signin_message = f"Triggering punch with mode of work: '{mode_of_work}'"
        print(signin_message)
        output = signin(driver, mode_of_work)  # trigger the selenium function for work from home
        print(output)
        send_email("Punch Report", signin_message + "\n" + output)

    elif current_day in ['thursday', 'friday']:
        mode_of_work = "work from office."
        signin_message = f"Triggering signin with mode of work: '{mode_of_work}'"
        print(signin_message)
        output = signin(driver, mode_of_work)  # trigger the selenium function for work from office
        print(output)
        send_email("Punch Report", signin_message + "\n" + output)

    else:
        weekend_message = "Today is Saturday or Sunday. No sign-in or sign-out will be triggered."
        print(weekend_message)
        send_email("Punch Report - Weekend Notice", weekend_message)

main(driver)
