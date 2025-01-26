from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Set up Firefox options
options = Options()
options.headless = True

# Initialize WebDriver for Firefox
service = FirefoxService()
driver = webdriver.Firefox(service=service, options=options)

def check_and_click_secondary_btn():
    """Check if 'btn btn-secondary w-100 mt-2' appears and click it."""
    try:
        secondary_btn = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "btn.btn-secondary.w-100.mt-2"))
        )
        secondary_btn.click()
        print('Dynamic click: "btn btn-secondary w-100 mt-2".')
    except Exception:
        pass  # Ignore if the button doesn't appear

try:
    # -------------------------------------------------------------------------
    # 1) Open the website and handle the initial steps (cookies, register div)
    # -------------------------------------------------------------------------
    driver.get("https://mike.larsson.cz/")
    wait = WebDriverWait(driver, 10)

    # Accept cookies if the button is present
    try:
        accept_cookies_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btnAcceptAll")))
        accept_cookies_btn.click()
        print("Cookies accepted.")
    except Exception:
        print("No cookie banner found.")

    # Click the register content div (if present)
    try:
        register_div = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "register_content.alt_rss.doppelt_in_basket.animated"))
        )
        register_div.click()
        print('Clicked "register_content.alt_rss.doppelt_in_basket.animated".')
    except Exception:
        print('"register_content.alt_rss.doppelt_in_basket.animated" not found.')

    # Continuously check if the secondary button appears
    check_and_click_secondary_btn()
    time.sleep(2)

    # -------------------------------------------------------------------------
    # 2) Click the checkbox using JavaScript
    # -------------------------------------------------------------------------
    checkbox = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "form-check-input.shadow-none")))
    driver.execute_script("arguments[0].click();", checkbox)
    print("Checkbox clicked via JavaScript.")
    check_and_click_secondary_btn()

    # -------------------------------------------------------------------------
    # 3) Find the categories under #productsMenu in *both* formats
    # -------------------------------------------------------------------------
    products_menu = wait.until(EC.presence_of_element_located((By.ID, "productsMenu")))
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 3a) Old-style categories:
    old_style_categories = soup.find_all(
        "div",
        class_="d-flex flex-grow-1 link-dark rounded green-menu-item left-menu-item ms-0"
    )

    # 3b) New-style categories (div-menu-item):
    new_style_categories = soup.find_all(
        "div",
        class_="d-flex flex-grow-1 flex-row align-items-center justify-content-between rounded div-menu-item"
    )

    category_links = []

    for cat in old_style_categories:
        a_tag = cat.find("a", href=True)
        if a_tag:
            category_links.append(a_tag["href"])

    for cat in new_style_categories:
        a_tag = cat.find("a", href=True)
        if a_tag:
            category_links.append(a_tag["href"])

    print("Found category links:")
    for c in category_links:
        print(" -", c)

    # -------------------------------------------------------------------------
    # 4) For each category link, visit and scrape product data
    # -------------------------------------------------------------------------
    for link in category_links:
        print(f"\nNavigating to category: {link}")
        driver.get(link)
        time.sleep(2)
        check_and_click_secondary_btn()

        # Check for 'active' category div
        try:
            active_cat_div = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.d-flex.flex-grow-1.active.rounded.green-menu-item.left-menu-item.ms-0")
                )
            )
            active_cat_div.click()
            print('Clicked the "active" category div.')
            time.sleep(2)
            check_and_click_secondary_btn()
        except Exception:
            print("No active category div found (or not clickable).")

        # Parse with BeautifulSoup
        category_soup = BeautifulSoup(driver.page_source, "html.parser")

        # Each product is in class="card-body d-flex
        card_bodies = category_soup.find_all(
            "div",
            class_="card-body d-flex flex-column flex-md-row justify-content-between justify-content-lg-evenly justify-content-xl-between"
        )

        # Extract product names from class="green-color"
        for cb in card_bodies:
            link_tag = cb.find("a", class_="green-color")
            if link_tag:
                product_name = link_tag.get_text(strip=True)
                print(f"Product Name: {product_name}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # -------------------------------------------------------------------------
    # 5) Close the driver
    # -------------------------------------------------------------------------
    driver.quit()
