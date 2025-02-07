import pandas as pd
import ftplib
import requests
import base64

# === STEP 1: Load CSV File ===
input_file = "testproducts1.csv"
output_file = "all_products_wp.csv"

# Read CSV
df = pd.read_csv(input_file)

# === STEP 2: Transform Data for WP All Import ===
rename_map = {
    "Name": "post_title",
    "Selling Price": "regular_price",
    "Price Without Tax": "price_excl_tax",
    "Category": "product_cat",
}

# Rename columns
df = df.rename(columns=rename_map)

# Add necessary WooCommerce fields
df["post_status"] = "publish"  # Publish product
df["post_type"] = "product"  # WooCommerce requires this
df["sku"] = df["post_title"].str.replace(" ", "-").str.lower()  # Generate SKU

# Save transformed file
df.to_csv(output_file, index=False)
print(f"Transformed file saved as: {output_file}")

# === STEP 3: Upload to WordPress via FTP (Optional) ===
ftp_enabled = False  # Set to True to enable FTP upload

if ftp_enabled:
    FTP_HOST = "your-ftp-host.com"
    FTP_USER = "your-ftp-username"
    FTP_PASS = "your-ftp-password"
    FTP_PATH = "/wp-content/uploads/all_products_wp.csv"

    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)

    with open(output_file, "rb") as file:
        ftp.storbinary(f"STOR {FTP_PATH}", file)

    ftp.quit()
    print(f"File uploaded to: {FTP_PATH}")

# === STEP 4: Trigger WP All Import via API (Optional) ===
wp_api_enabled = False  # Set to True to trigger WP All Import API

if wp_api_enabled:
    WP_SITE = "https://motoguys.sk"
    WP_ADMIN = "mage_in4q9ldf"
    WP_PASSWORD = "WbTZz@q$ib03hnh8"

    # Encode credentials
    credentials = f"{WP_ADMIN}:{WP_PASSWORD}"
    token = base64.b64encode(credentials.encode())

    headers = {"Authorization": f"Basic {token.decode('utf-8')}"}

    # Upload CSV via API
    upload_url = f"{WP_SITE}/wp-json/wp/v2/media"

    with open(output_file, "rb") as file:
        response = requests.post(upload_url, headers=headers, files={"file": file})

    if response.status_code == 201:
        print("CSV uploaded successfully.")
        media_id = response.json()["id"]

        # Trigger WP All Import
        import_url = f"{WP_SITE}/wp-json/wpai/v1/import/run"
        import_response = requests.post(import_url, headers=headers, json={"import_id": media_id})

        if import_response.status_code == 200:
            print("WP All Import triggered successfully.")
        else:
            print("Failed to trigger WP All Import:", import_response.text)
    else:
        print("Failed to upload CSV:", response.text)

print("Done! Go to WP All Import to start the import manually if needed.")
