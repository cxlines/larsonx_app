import os
import glob
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve credentials
USERNAME = os.getenv("WP_ADMIN_USERNAME")
PASSWORD = os.getenv("WP_ADMIN_PASSWORD")

# Ensure credentials exist
if not USERNAME or not PASSWORD:
    raise ValueError("ERROR: Missing WP_ADMIN_USERNAME or WP_ADMIN_PASSWORD in .env file!")

# WordPress admin URL
WP_ADMIN_URL = "https://motoguys.sk/wp-admin/"

# Get the script's directory and set `latestproducts` path
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
CSV_DIRECTORY = os.path.join(SCRIPT_DIRECTORY, "latestproducts")


# Function to get the latest CSV file
def get_latest_csv(directory):
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return None

    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    if not csv_files:
        print("No CSV files found.")
        return None

    latest_file = max(csv_files, key=os.path.getmtime)
    print(f"Latest CSV File Selected: {latest_file}")
    return latest_file


# Get the latest CSV file
CSV_FILE_PATH = get_latest_csv(CSV_DIRECTORY)

# Ensure there is a CSV file to upload
if not CSV_FILE_PATH:
    print("No CSV file found. Exiting.")
    exit()

# Start Selenium WebDriver
driver = webdriver.Firefox()

try:
    wait = WebDriverWait(driver, 10)  # Explicit wait

    # Open WordPress Admin login page
    driver.get(WP_ADMIN_URL)

    # Wait for login fields and enter credentials
    wait.until(EC.presence_of_element_located((By.ID, "user_login"))).send_keys(USERNAME)
    wait.until(EC.presence_of_element_located((By.ID, "user_pass"))).send_keys(PASSWORD)

    # Click login button
    driver.find_element(By.ID, "wp-submit").click()

    # Wait until the admin dashboard is loaded (or check for login failure)
    if not wait.until(EC.presence_of_element_located((By.ID, "wp-admin-bar-site-name"))):
        print("Login failed! Please check your credentials.")
        exit()

    print("Login successful!")

    # Navigate to Media Upload Page
    driver.get("https://motoguys.sk/wp-admin/media-new.php")

    # Wait for the file upload input field
    upload_input = wait.until(EC.presence_of_element_located((By.NAME, "async-upload")))

    # Upload the file
    upload_input.send_keys(CSV_FILE_PATH)

    # Click Upload button
    driver.find_element(By.ID, "html-upload").click()

    # Wait for the upload to complete (check for success message or progress bar)
    time.sleep(8)  # Adjust based on upload time
    print("File uploaded successfully!")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()
