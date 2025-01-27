import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Replace with your actual credentials
USERNAME = "601200"
PASSWORD = "s2032ab15"


# Function to initialize Firefox WebDriver
def initialize_driver():
    # Set up Firefox options
    options = Options()
    options.headless = True  # Run in headless mode if desired

    # Initialize WebDriver for Firefox
    service = FirefoxService()
    driver = webdriver.Firefox(service=service, options=options)
    return driver


# Function to scrape products from a category
def scrape_category_products(driver, category_url):
    driver.get(category_url)
    wait = WebDriverWait(driver, 10)

    # Wait for product cards to load
    product_cards = wait.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "col.d-flex.tgm-gal-box.mb-3")
    ))

    products = []
    for card in product_cards:
        try:
            # Extract product name
            product_name = card.find_element(By.CLASS_NAME, "card-title.cut-text.pe-1.mb-0").find_element(By.CLASS_NAME,
                                                                                                          "green-color").text.strip()

            # Extract selling price
            selling_price = card.find_element(By.CLASS_NAME, "card-text.fw-bold1.mb-0").text.strip()

            # Extract price without tax
            price_without_tax = card.find_element(By.CLASS_NAME,
                                                  "card-text.gal-preis-ek.gal_price_color.fw-600_1.fw-bold.mb-0").find_element(
                By.TAG_NAME, "span").text.strip()

            # Append product details
            products.append({
                "Name": product_name,
                "Selling Price": selling_price,
                "Price Without Tax": price_without_tax
            })
        except Exception as e:
            print(f"Error extracting product: {e}")
            continue

    return products


# Main script
try:
    # Initialize the WebDriver
    driver = initialize_driver()

    # Open the website
    driver.get("https://mike.larsson.cz/")

    # Wait for the accept cookies button to be present and click it
    wait = WebDriverWait(driver, 10)
    accept_cookies_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btnAcceptAll")))
    accept_cookies_button.click()
    print("Accepted cookies")

    # Find the username and password input fields
    username_field = wait.until(EC.presence_of_element_located((By.NAME, "mcustno")))
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "mpassword")))

    # Enter credentials
    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)
    print("Entered credentials")

    # Submit the form
    password_field.send_keys(Keys.RETURN)
    print("Submitted login form")

    # Wait for the page to refresh and load the new look
    time.sleep(5)

    # Locate the checkbox (div) and click it
    checkbox = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "form-check-input.shadow-none")))
    checkbox.click()
    print("Clicked the checkbox!")

    # Locate all <a> elements with the specified class name
    links = wait.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "d-flex.flex-grow-1.link-dark.rounded.green-menu-item.left-menu-item.ms-0")
    ))

    # Extract links and names
    categories = []
    for link in links:
        category_name = link.text.strip()  # Extract category name
        category_url = link.get_attribute("href")  # Extract category URL
        categories.append({"name": category_name, "url": category_url})

    # Scrape products from each category and save to CSV
    all_products = []
    for category in categories:
        print(f"Scraping category: {category['name']} -> {category['url']}")
        products = scrape_category_products(driver, category['url'])
        for product in products:
            product["Category"] = category["name"]  # Add category name to each product
        all_products.extend(products)

    # Save products to CSV
    with open("all_products.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Name", "Selling Price", "Price Without Tax", "Category"])
        writer.writeheader()
        writer.writerows(all_products)

    print("Products saved to all_products.csv")

finally:
    # Close the browser
    try:
        driver.quit()
    except NameError:
        print("Driver not initialized, skipping quit.")
