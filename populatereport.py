import os
import time
import mysql.connector
import psutil
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

##############################################################################
# 1) ENVIRONMENT & CONFIG
##############################################################################
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
# 2) SETUP SELENIUM
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

def update_compliance_type_if_exists(claim_number, compliance_report_type):
    """
    Updates 'compliance_report_type' only if the claim_number already exists in DB.
    If no row is found for claim_number, we do NOTHING (no insert).
    """
    try:
        # Check if the claim_number currently exists:
        db_cursor.execute(
            "SELECT id, claim_number FROM claims WHERE claim_number = %s",
            (claim_number,)
        )
        row = db_cursor.fetchone()

        if row is None:
            # No existing record for this claim_number, skip insertion
            print(f"[SKIP] Claim {claim_number} not in DB; skipping update.")
            return

        # If found, do an update:
        update_sql = """
            UPDATE claims
            SET compliance_report_type = %s
            WHERE claim_number = %s
        """
        db_cursor.execute(update_sql, (compliance_report_type, claim_number))
        db_connection.commit()

        print(f"[DB] Updated claim_number={claim_number} => compliance_report_type={compliance_report_type}")

    except Exception as e:
        print(f"[ERROR][DB] {e}")

##############################################################################
# 4) MAIN LOGIC
##############################################################################
try:
    print("[INFO] Logging in to CNC Claimsource...")
    driver.get("https://www.cnc-claimsource.com/index.php?LOG_OUT_USER=149")

    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "username")))
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)

    login_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginBtn")))
    login_btn.click()

    WebDriverWait(driver, 15).until(EC.url_contains("examiner_portal"))
    print("[INFO] Login successful.")

    # Go to compliance page
    driver.get("https://www.cnc-claimsource.com/rpt/rpt_compliance.php")

    # Click 'Submitted' if that's how you load the table
    submitted_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.ID, "submitted"))
    )
    submitted_btn.click()

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//tbody"))
    )

    print("[INFO] Starting to parse compliance rows...")

    page_count = 1

    while True:
        # Check system resources
        if not check_system_resources():
            print("[PAUSE] High resource usage. Sleeping 30s.")
            time.sleep(30)

        # Gather rows
        rows = driver.find_elements(By.XPATH, "//tbody/tr")
        print(f"[INFO] Page {page_count}: Found {len(rows)} rows.")

        for i, row in enumerate(rows, start=1):
            try:
                # The link that leads to notes => has cid=??? in the href
                claim_link = row.find_element(By.XPATH, ".//td/a[contains(@href, 'pg=notes')]")
                claim_href = claim_link.get_attribute("href")
                claim_number = claim_href.split("cid=")[1]

                # The compliance link => has rtype=??? in the href
                compliance_report_link = row.find_element(By.XPATH, ".//td/a[contains(@href, 'compliance.php')]")
                compliance_report_href = compliance_report_link.get_attribute("href")

                if "rtype=" in compliance_report_href:
                    rtype_part = compliance_report_href.split("rtype=")[1]
                    compliance_report_type = rtype_part.split("&")[0]
                else:
                    compliance_report_type = "unknown"

                print(f"[DEBUG] Row {i}: claim_number={claim_number}, type={compliance_report_type}")

                # Only update existing
                update_compliance_type_if_exists(claim_number, compliance_report_type)

            except NoSuchElementException:
                print(f"[ERROR] Row {i}: Missing link(s). Skipping row.")
                continue
            except Exception as row_e:
                print(f"[ERROR] Row {i} unexpected error: {row_e}")
                continue

        # Attempt "Next »" to see if there's another page
        page_count += 1
        try:
            next_button = driver.find_element(By.LINK_TEXT, "Next »")
            next_button.click()
            time.sleep(2)
        except NoSuchElementException:
            print("[INFO] No more pages of compliance data.")
            break

    print("[SUCCESS] Finished updating compliance_report_type for existing rows.")

except Exception as e:
    print(f"[FATAL] Unexpected error: {e}")
finally:
    driver.quit()
    db_cursor.close()
    db_connection.close()
    print("[INFO] Script complete.")
