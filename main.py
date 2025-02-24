import csv
import datetime
import subprocess
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv

load_dotenv()


# Retrieve credentials
USERNAME = os.getenv("MIKEUSERNAME")
PASSWORD = os.getenv("MIKEPASSWORD")

def initialize_driver():
    options = Options()
    options.headless = True
    service = FirefoxService()
    driver = webdriver.Firefox(service=service, options=options)
    return driver


def handle_human_verification(driver):
    try:
        wait = WebDriverWait(driver, 5)
        verification_checkbox = wait.until(EC.presence_of_element_located((By.XPATH, "//div/label/input")))
        verification_checkbox.click()
        print("Clicked human verification checkbox!")
        time.sleep(2)
    except Exception as e:
        print(f"No human verification checkbox found or other error: {e}")


def scrape_category_products(driver, category_url):
    wait = WebDriverWait(driver, 10)
    pagenumber = 0
    products = []
    empty_pages = 0

    while True:
        current_url = f"{category_url}?sr={pagenumber}&show=list"
        print(f"Scraping page: {current_url}")
        driver.get(current_url)
        time.sleep(2)
        handle_human_verification(driver)

        try:
            product_cards = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "col.d-flex.tgm-gal-box.mb-3")))
            empty_pages = 0
        except Exception:
            print(f"No products found on page: {current_url}")
            empty_pages += 1
            if empty_pages >= 2:
                print("2 consecutive empty pages. Moving to the next category.")
                break
            pagenumber += 30
            continue

        for card in product_cards:
            try:
                product_name = card.find_element(By.CLASS_NAME, "card-title.compact-name1.mb-3.mt-1").find_element(
                    By.CLASS_NAME, "green-color1").text.strip()
                selling_price = card.find_element(By.CLASS_NAME, "card-text.fw-bold1.mb-0").text.strip()
                price_without_tax = card.find_element(By.CLASS_NAME,
                                                      "card-text.gal-preis-ek.gal_price_color.fw-600_1.fw-bold.mb-0").find_element(
                    By.TAG_NAME, "span").text.strip()

                delivery_date = card.find_element(By.CLASS_NAME, "color-inherit1.lh-1").text.strip()
                product_state = card.find_element(By.CLASS_NAME, "bg-middle-gray.ps-1.pe-1").text.strip()
                product_code = card.find_element(By.CLASS_NAME, "fw-bold").text.strip()
                product_image = card.find_element(By.CLASS_NAME,
                                                             "figure-img.img-fluid.m-0.height-100").get_attribute("src")

                products.append({
                    "Name": product_name,
                    "Selling Price": selling_price,
                    "Price Without Tax": price_without_tax,
                    "Delivery Date": delivery_date,
                    "Product State": product_state,
                    "Product Code": product_code,
                    "Product Image": product_image
                })
            except Exception as e:
                print(f"Error scraping product: {e}")

        print(f"Scraped {len(product_cards)} products from page: {current_url}")
        pagenumber += 30

    return products


try:
    driver = initialize_driver()
    driver.get("https://mike.larsson.cz/")
    handle_human_verification(driver)
    wait = WebDriverWait(driver, 10)

    accept_cookies_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btnAcceptAll")))
    accept_cookies_button.click()
    print("Accepted cookies")
    handle_human_verification(driver)

    username_field = wait.until(EC.presence_of_element_located((By.NAME, "mcustno")))
    password_field = wait.until(EC.presence_of_element_located((By.NAME, "mpassword")))

    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)
    print("Entered credentials")
    password_field.send_keys(Keys.RETURN)
    print("Submitted login form")

    handle_human_verification(driver)
    time.sleep(5)

    checkbox = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "form-check-input.shadow-none")))
    checkbox.click()
    print("Clicked the checkbox!")

    handle_human_verification(driver)
    links = wait.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "d-flex.flex-grow-1.link-dark.rounded.green-menu-item.left-menu-item.ms-0")))

    categories = []
    for link in links:
        category_name = link.text.strip()
        category_url = link.get_attribute("href")
        categories.append({"name": category_name, "url": category_url})

    all_products = []
    for category in categories:
        print(f"Scraping category: {category['name']} -> {category['url']}")
        products = scrape_category_products(driver, category['url'])
        for product in products:
            product["Category"] = category["name"]
        all_products.extend(products)

    os.makedirs("latestproducts", exist_ok=True)
    filename = os.path.join("latestproducts",
                            f"all_products_wp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Name", "Selling Price", "Price Without Tax", "Delivery Date",
                                                  "Product State", "Product Code", "Product Image", "Category"])
        writer.writeheader()
        writer.writerows(all_products)

    print(f"Products saved to {filename}")

    subprocess.run([sys.executable, "product_transform.py"], check=True)
    print("product_transform.py executed successfully.")

finally:
    try:
        driver.quit()
    except NameError:
        print("Driver not initialized, skipping quit.")