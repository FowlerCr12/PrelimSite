import os
import time
import mysql.connector
import psutil
import boto3
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

##############################################################################
# 1) ENVIRONMENT & CONFIG
##############################################################################

# Load .env if you keep secrets there; otherwise, hard-code below
load_dotenv()

USERNAME = "craigfowler"
PASSWORD = r"Skipper6816!!!"

DB_HOST = "prelim-program-database-do-user-18860734-0.f.db.ondigitalocean.com"
DB_PORT = 25060  # typical DO MySQL port
DB_USER = "doadmin"
DB_PASSWORD = "AVNS_M6ypXrCa1JjgD65mbBX"
DB_NAME = "defaultdb"

def check_system_resources(threshold=90):
    """Return False if memory usage exceeds `threshold`%."""
    mem = psutil.virtual_memory()
    if mem.percent > threshold:
        print(f"[WARN] High memory usage: {mem.percent}% > {threshold}% threshold")
        return False
    return True


##############################################################################
# 2) SETUP SELENIUM (HEADLESS CHROME)
##############################################################################
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--disable-breakpad")

driver = webdriver.Chrome(options=options)


##############################################################################
# 3) SETUP MYSQL
##############################################################################
db_connection = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
db_cursor = db_connection.cursor()

def upsert_compliance_type(claim_number, compliance_report_type):
    """
    Insert or update compliance_report_type for the given claim_number.
    If your table is set up to allow multiple compliance types per claim, 
    ensure you have a UNIQUE KEY on (claim_number, compliance_report_type).
    """
    try:
        sql = """
            INSERT INTO claims (claim_number, compliance_report_type)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
              compliance_report_type = VALUES(compliance_report_type)
        """
        db_cursor.execute(sql, (claim_number, compliance_report_type))
        db_connection.commit()
        print(f"[DB] Upserted claim_number={claim_number}, compliance_report_type={compliance_report_type}")
    except Exception as e:
        print(f"[ERROR][DB] {e}")


##############################################################################
# 4) MAIN LOGIC
##############################################################################
try:
    print("[INFO] Logging in to CNC Claimsource...")
    driver.get("https://www.cnc-claimsource.com/index.php?LOG_OUT_USER=149")

    # Wait for login fields
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)

    # Click login
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "loginBtn"))
    )
    login_btn.click()

    # Wait for examiner portal
    WebDriverWait(driver, 15).until(EC.url_contains("examiner_portal"))
    print("[INFO] Login successful.")

    # Go to compliance page
    print("[INFO] Navigating to compliance page...")
    driver.get("https://www.cnc-claimsource.com/rpt/rpt_compliance.php")

    # Optionally filter or click "Submitted" if needed
    submitted_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "submitted"))
    )
    submitted_btn.click()

    # Wait for table
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//tbody"))
    )

    print("[INFO] Starting to parse compliance rows...")

    while True:
        # Check system resources
        if not check_system_resources():
            print("[PAUSE] High resource usage. Sleeping 30s.")
            time.sleep(30)

        # Gather rows
        rows = driver.find_elements(By.XPATH, "//tbody/tr")
        print(f"[INFO] Found {len(rows)} rows on this page.")

        for row in rows:
            try:
                # Claim number is typically in a link with "pg=notes" param
                claim_link = row.find_element(By.XPATH, ".//td/a[contains(@href, 'pg=notes')]")
                claim_href = claim_link.get_attribute("href")
                claim_number = claim_href.split("cid=")[1]

                # The compliance link has "compliance.php" with `rtype=xxx`
                compliance_report_link = row.find_element(By.XPATH, ".//td/a[contains(@href, 'compliance.php')]")
                compliance_report_href = compliance_report_link.get_attribute("href")

                # Extract rtype=...
                # Typically something like: ...compliance.php?rtype=15_day&cid=1234
                # We'll just grab what's after `rtype=`
                if "rtype=" in compliance_report_href:
                    compliance_report_type = compliance_report_href.split("rtype=")[1].split("&")[0]
                else:
                    compliance_report_type = "unknown"

                # Upsert into DB
                upsert_compliance_type(claim_number, compliance_report_type)

            except NoSuchElementException:
                # Probably a row with unexpected format
                continue
            except Exception as row_e:
                print(f"[ERROR] Row parsing error: {row_e}")
                continue

        # Attempt "Next »" to see if there's another page
        try:
            next_button = driver.find_element(By.LINK_TEXT, "Next »")
            next_button.click()
            time.sleep(2)
        except NoSuchElementException:
            # No more pages
            print("[INFO] No more pages of compliance data.")
            break

    print("[SUCCESS] Finished populating compliance_report_type for all found rows.")

except Exception as e:
    print(f"[FATAL] Unexpected error: {e}")
finally:
    driver.quit()
    db_cursor.close()
    db_connection.close()
    print("[INFO] Script complete.")
