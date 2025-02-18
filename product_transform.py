
import os
import glob
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Admin Credentials
WP_ADMIN_URL = "https://motoguys.sk/wp-admin/"
USERNAME = "mage_in4q9ldf"
PASSWORD = "WbTZz@q$ib03hnh8"

# Directory containing CSV files
CSV_DIRECTORY = "C:/Users/mulle/Desktop/JASPRAVIM25/patricius12/LarsonX/latestproducts"

# get the latest CSV file
def get_latest_csv(directory):
    csv_files = glob.glob(os.path.join(directory, "*.csv"))

    if not csv_files:
        print("No CSV files found in the directory.")
        return None

    latest_file = max(csv_files, key=os.path.getmtime)
    print(f"Latest CSV File Selected: {latest_file}")
    return latest_file

# Find the latest CSV
CSV_FILE_PATH = get_latest_csv(CSV_DIRECTORY)

if CSV_FILE_PATH:  # Proceed only if a file is found
    # Start Selenium WebDriver
    driver = webdriver.Firefox()

    try:
        # Open WordPress Admin
        driver.get(WP_ADMIN_URL)
        time.sleep(2)

        driver.find_element(By.ID, "user_login").send_keys(USERNAME)
        driver.find_element(By.ID, "user_pass").send_keys(PASSWORD)
        driver.find_element(By.ID, "wp-submit").click()
        time.sleep(3)

        # Navigate to Media Upload Page
        driver.get("https://motoguys.sk/wp-admin/media-new.php")
        time.sleep(2)

        # Upload the latest CSV File
        upload_input = driver.find_element(By.NAME, "async-upload")
        upload_input.send_keys(CSV_FILE_PATH)  # Upload file
        time.sleep(2)

        # Click
        driver.find_element(By.ID, "html-upload").click()
        time.sleep(5)

        print("File uploaded successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

else:
    print("No CSV file found. Exiting.")
