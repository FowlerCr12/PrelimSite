import os
import time
import requests
import PyPDF2
import boto3
import mysql.connector  # for MySQL
import psutil

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from dotenv import load_dotenv

###########################################
# CONFIGURATION
###########################################
# Load environment variables first
load_dotenv()

# DigitalOcean Spaces
SPACES_KEY = os.getenv('SPACES_KEY')     # <-- removed the trailing comma
SPACES_SECRET = os.getenv('SPACES_SECRET')
SPACES_ENDPOINT = "nyc3.digitaloceanspaces.com"
SPACES_BUCKET = "prelim-program-file-storage"
SPACES_REGION = "nyc3"

# Website login
USERNAME = "craigfowler"
PASSWORD = r"Skipper6816&&&"

# Local folders
NOTES_FOLDER = "downloads/notes"
PDF_FOLDER = "downloads/pdfs"
os.makedirs(NOTES_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

# MySQL Database Info (replace with your actual DO MySQL credentials)
DB_HOST = "prelim-program-database-do-user-18860734-0.f.db.ondigitalocean.com"
DB_PORT = 25060  # typical DO MySQL port
DB_USER = "doadmin"
DB_PASSWORD = "AVNS_M6ypXrCa1JjgD65mbBX"
DB_NAME = "defaultdb"

###########################################
# DO SPACES HELPERS
###########################################
def check_system_resources():
    """Return False if memory usage exceeds 90%"""
    mem = psutil.virtual_memory()
    if mem.percent > 90:
        print(f"[WARN] High memory usage: {mem.percent}%")
        return False
    return True

def get_s3_client():
    session = boto3.session.Session()
    return session.client(
        "s3",
        region_name=SPACES_REGION,
        endpoint_url=f"https://{SPACES_ENDPOINT}",
        aws_access_key_id=SPACES_KEY,
        aws_secret_access_key=SPACES_SECRET,
    )

def upload_file_to_spaces(local_file_path, bucket_name, object_key=None, ExtraArgs={"ACL": "public-read"}):
    """
    Upload local_file_path to the specified bucket at object_key.
    Returns object_key on success, or None on failure.
    """
    if not os.path.exists(local_file_path):
        print(f"[WARNING] File does not exist for upload: {local_file_path}")
        return None

    if object_key is None:
        object_key = os.path.basename(local_file_path)

    s3_client = get_s3_client()
    try:
        s3_client.upload_file(local_file_path, bucket_name, object_key)
        print(f"[DEBUG] Uploaded {local_file_path} to {bucket_name}/{object_key}")
        return object_key
    except Exception as e:
        print(f"[ERROR] Uploading {local_file_path} to Spaces: {e}")
        return None

def get_spaces_public_url(object_key):
    """
    For a public bucket:
    https://<BUCKETNAME>.<ENDPOINT>/<OBJECT_KEY>
    """
    return f"https://{SPACES_BUCKET}.{SPACES_ENDPOINT}/{object_key}"

###########################################
# SELENIUM SETUP
###########################################
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")  # Disable GPU acceleration
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-software-rasterizer")  # Disable unnecessary components
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--disable-breakpad")

prefs = {
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)

###########################################
# PDF DOWNLOAD & PROCESSING
###########################################
def download_pdf_via_requests(pdf_url, cid):
    """
    Use requests w/ Selenium session cookies to download PDF to PDF_FOLDER/<cid>_temp.pdf.
    Returns local file path or None if failed.
    """
    print(f"[DEBUG] Attempting direct download for Claim {cid}: {pdf_url}")

    # Grab cookies from Selenium to stay authenticated
    selenium_cookies = driver.get_cookies()
    cookie_jar = requests.cookies.RequestsCookieJar()
    for c in selenium_cookies:
        cookie_jar.set(c['name'], c['value'], domain=c['domain'])
        print(f"[DEBUG] Added cookie: {c['name']}")

    local_path = os.path.join(PDF_FOLDER, f"{cid}_temp.pdf")
    try:
        print(f"[DEBUG] Sending GET request to {pdf_url}")
        resp = requests.get(pdf_url, cookies=cookie_jar, stream=True, timeout=30)
        print(f"[DEBUG] Response status code: {resp.status_code}")
        print(f"[DEBUG] Response headers: {resp.headers}")
        
        if resp.status_code == 200:
            content_type = resp.headers.get('content-type', '')
            if 'pdf' not in content_type.lower():
                print(f"[WARNING] Response may not be PDF. Content-Type: {content_type}")
            
            with open(local_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify file was created and has content
            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                print(f"[DEBUG] Successfully downloaded PDF for Claim {cid} to {local_path}")
                time.sleep(2)
                return local_path
            else:
                print(f"[ERROR] Downloaded file is empty or missing: {local_path}")
        else:
            print(f"[ERROR] Claim {cid} PDF request failed with status={resp.status_code}")
            print(f"[ERROR] Response text: {resp.text[:500]}")  # First 500 chars of error response
    except Exception as e:
        print(f"[ERROR] Downloading PDF for Claim {cid}: {str(e)}")
        import traceback
        print(f"[ERROR] Full traceback: {traceback.format_exc()}")

    return None

def extract_single_page_pdf(input_pdf_path, output_pdf_path):
    """
    Reads 'input_pdf_path' and writes only the first page to 'output_pdf_path'.
    Returns True if successful, False otherwise.
    """
    try:
        reader = PyPDF2.PdfReader(input_pdf_path)
        writer = PyPDF2.PdfWriter()

        if len(reader.pages) == 0:
            print(f"[ERROR] {input_pdf_path} has 0 pages.")
            return False

        writer.add_page(reader.pages[0])  # just the first page
        with open(output_pdf_path, "wb") as out:
            writer.write(out)
        return True
    except Exception as e:
        print(f"[ERROR] Could not extract first page from {input_pdf_path}: {e}")
        return False

def extract_first_7_pages_from_pdf(pdf_path):
    text_content = []
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page_idx in range(min(7, len(reader.pages))):
                page = reader.pages[page_idx]
                text_content.append(page.extract_text())
                page = None  # Help GC
        return "\n".join(text_content).strip()
    except Exception as e:
        print(f"[ERROR] Extracting text from {pdf_path}: {e}")
        return ""

def extract_proof_of_loss_page(final_pdf_path, prelim_pdf_path, output_path, search_text="Proof Of Loss"):
    """
    Extract Proof of Loss page from final_pdf_path and append it to prelim_pdf_path,
    saving the result to output_path.
    Returns True if successful, False otherwise.
    """
    try:
        # Open the Final Report to find Proof of Loss page
        with open(final_pdf_path, "rb") as f:
            final_reader = PyPDF2.PdfReader(f)
            
            # Find the Proof of Loss page
            pol_page = None
            for page_index in range(len(final_reader.pages)):
                page = final_reader.pages[page_index]
                page_text = page.extract_text() or ""
                if search_text.lower() in page_text.lower():
                    pol_page = page
                    break
            
            if pol_page is None:
                print(f"[ERROR] No '{search_text}' page found in Final Report")
                return False
            
            # Open Prelim Binder and create merged PDF
            with open(prelim_pdf_path, "rb") as prelim_f:
                prelim_reader = PyPDF2.PdfReader(prelim_f)
                pdf_writer = PyPDF2.PdfWriter()
                
                # Add all pages from Prelim Binder
                for page in prelim_reader.pages:
                    pdf_writer.add_page(page)
                
                # Add the Proof of Loss page
                pdf_writer.add_page(pol_page)
                
                # Save the merged PDF
                with open(output_path, "wb") as out_f:
                    pdf_writer.write(out_f)
                
                print(f"[DEBUG] Successfully appended Proof of Loss page to {output_path}")
                return True
                
    except Exception as e:
        print(f"[ERROR] Failed to extract and append Proof of Loss page: {e}")
        return False

###########################################
# MYSQL DB SETUP
###########################################
# We'll create a connection here and reuse it in store_in_db
db_connection = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
db_cursor = db_connection.cursor()

def store_in_db(cid, notes_spaces_link, binder_spaces_link):
    """
    Insert or update your row in the 'claims' table.
    """
    try:
        insert_sql = """
            INSERT INTO claims (claim_number, notes_spaces_link, binder_spaces_link)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
              notes_spaces_link = VALUES(notes_spaces_link),
              binder_spaces_link = VALUES(binder_spaces_link);
        """
        db_cursor.execute(insert_sql, (cid, notes_spaces_link, binder_spaces_link))
        db_connection.commit()
        print(f"[DB] Upserted Claim {cid} with notes={notes_spaces_link}, binder={binder_spaces_link}")
    except Exception as e:
        print(f"[ERROR][DB] Could not insert claim {cid} into DB: {e}")

###########################################
# MAIN LOGIC
###########################################
try:
    print("[DEBUG] Navigating to login page...")
    driver.get("https://www.cnc-claimsource.com/index.php?LOG_OUT_USER=149")

    print("[DEBUG] Waiting for username field...")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "username")))

    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)

    print("[DEBUG] Clicking login button...")
    login_btn = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.ID, "loginBtn"))
    )
    login_btn.click()

    print("[DEBUG] Wait for examiner_portal URL part...")
    WebDriverWait(driver, 15).until(EC.url_contains("examiner_portal"))

    print("[DEBUG] Loading compliance page...")
    driver.get("https://www.cnc-claimsource.com/rpt/rpt_compliance.php")

    select_elem = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ico"))
    )
    Select(select_elem).select_by_visible_text("Centauri Specialty Insurance")

    submitted_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "submitted"))
    )
    submitted_btn.click()

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//tbody"))
    )

    # Loop pages until no next button
    while True:
        if not check_system_resources():
            print("[PAUSE] Waiting 30s for resource recovery...")
            time.sleep(30)
            continue
    
        rows = driver.find_elements(By.XPATH, "//tbody/tr")
        print(f"[DEBUG] Found {len(rows)} claims to process on this page")

        # Process all rows on this page
        for row in rows:
            try:
                claim_link = row.find_element(By.XPATH, ".//td/a[contains(@href, 'pg=notes')]")
                claim_href = claim_link.get_attribute("href")
                cid = claim_href.split("cid=")[1]

                notes_file_path = os.path.join(NOTES_FOLDER, f"{cid}.txt")
                has_final_path = os.path.join(NOTES_FOLDER, f"{cid}hasFinalReport.txt")

                # Skip if we've processed this claim before
                if os.path.exists(notes_file_path) or os.path.exists(has_final_path):
                    print(f"[DEBUG] Claim {cid} already processed, skipping.")
                    continue

                print(f"\n[DEBUG] Processing Claim {cid}")
                notes_spaces_link = None
                binder_spaces_link = None

                original_tab = driver.current_window_handle
                # open new tab
                driver.execute_script("window.open(arguments[0], '_blank');", claim_href)
                time.sleep(1)

                all_tabs = driver.window_handles
                if len(all_tabs) < 2:
                    print(f"[ERROR] Could not open new tab for Claim {cid}, skipping.")
                    continue

                new_tab = [t for t in all_tabs if t != original_tab]
                if not new_tab:
                    print(f"[ERROR] new_tab is empty for {cid}, skipping.")
                    continue

                driver.switch_to.window(new_tab[0])

                # --- NOTES ---
                try:
                    driver.get(f"https://www.cnc-claimsource.com/claim.php?pg=notes&cid={cid}")
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "notebook"))
                    )
                    notes_elems = driver.find_elements(By.CLASS_NAME, "claim_note")
                    notes_content = [n.text.strip() for n in notes_elems]

                    with open(notes_file_path, "w", encoding="utf-8") as f:
                        for n in notes_content:
                            f.write(n + "\n\n")
                    print(f"[DEBUG] Saved notes to {notes_file_path}")

                    # Upload notes
                    notes_key = f"notes/{cid}.txt"
                    uploaded_key = upload_file_to_spaces(notes_file_path, SPACES_BUCKET, notes_key)
                    if uploaded_key:
                        notes_spaces_link = get_spaces_public_url(uploaded_key)

                except (TimeoutException, NoSuchElementException) as e:
                    print(f"[ERROR] Could not load notes for Claim {cid}, skipping claim. Error: {e}")
                    driver.close()
                    driver.switch_to.window(original_tab)
                    continue

                # --- FILES PAGE ---
                try:
                    print(f"[DEBUG] Loading files page for claim {cid}")
                    driver.get(f"https://www.cnc-claimsource.com/claim.php?pg=files&cid={cid}")
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'claimcenter')]"))
                    )
                    print(f"[DEBUG] Files page loaded successfully")

                    # NFIP Preliminary Binder - EXTRACT ONLY FIRST PAGE
                    try:
                        print("[DEBUG] Looking for Preliminary Binder link...")
                        prelim_link_el = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "NFIP Preliminary Binder"))
                        )
                        prelim_url = prelim_link_el.get_attribute("href")
                        print(f"[DEBUG] Found Preliminary Binder link: {prelim_url}")

                        # Try to get all PDF links for debugging
                        all_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
                        print(f"[DEBUG] All PDF links found: {[link.get_attribute('href') for link in all_links]}")

                        prelim_pdf_path = download_pdf_via_requests(prelim_url, cid)
                        if prelim_pdf_path:
                            print(f"[DEBUG] Successfully downloaded Preliminary Binder to {prelim_pdf_path}")
                            # 1) Extract single page
                            single_page_path = os.path.join(PDF_FOLDER, f"{cid}_firstpage.pdf")
                            success = extract_single_page_pdf(prelim_pdf_path, single_page_path)
                            # 2) Remove the original multi-page PDF
                            try:
                                os.remove(prelim_pdf_path)
                                print(f"[DEBUG] Removed original multi-page PDF for {cid}")
                            except Exception as del_e:
                                print(f"[ERROR] Removing multi-page PDF for {cid}: {del_e}")

                            if success:
                                # 3) Rename single-page PDF to {cid}.pdf
                                final_prelim_path = os.path.join(PDF_FOLDER, f"{cid}.pdf")
                                try:
                                    os.rename(single_page_path, final_prelim_path)
                                    print(f"[DEBUG] Single-page PDF renamed to {final_prelim_path} for {cid}")
                                except Exception as rename_e:
                                    print(f"[ERROR] Renaming single-page PDF for {cid}: {rename_e}")
                                    final_prelim_path = single_page_path

                                # 4) Upload single-page PDF to Spaces
                                binder_key = f"pdfs/{cid}.pdf"
                                uploaded_pdf_key = upload_file_to_spaces(final_prelim_path, SPACES_BUCKET, binder_key)
                                if uploaded_pdf_key:
                                    binder_spaces_link = get_spaces_public_url(uploaded_pdf_key)
                            else:
                                print(f"[ERROR] Could not extract single page from Prelim Binder for {cid}")
                        else:
                            print(f"[ERROR] Preliminary Binder download failed for {cid}")
                    except TimeoutException:
                        print(f"[DEBUG] No 'NFIP Preliminary Binder' found for {cid}")

                    # Final Report
                    try:
                        final_link_el = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Final Report"))
                        )
                        final_url = final_link_el.get_attribute("href")
                        print(f"[DEBUG] Found Final Report link: {final_url}")

                        final_pdf_path = download_pdf_via_requests(final_url, cid)
                        if final_pdf_path:
                            # Extract text for notes
                            fr_text = extract_first_7_pages_from_pdf(final_pdf_path)
                            with open(notes_file_path, "a", encoding="utf-8") as file:
                                file.write("\n\n===== Final Report Text (First 7 Pages) =====\n")
                                file.write(fr_text + "\n")

                            # If we have a prelim binder PDF, append Proof of Loss page
                            if binder_spaces_link:
                                prelim_path = os.path.join(PDF_FOLDER, f"{cid}.pdf")
                                merged_path = os.path.join(PDF_FOLDER, f"{cid}_with_pol.pdf")
                                
                                if extract_proof_of_loss_page(final_pdf_path, prelim_path, merged_path):
                                    # Upload the new merged PDF
                                    binder_key = f"pdfs/{cid}_with_pol.pdf"
                                    uploaded_pdf_key = upload_file_to_spaces(merged_path, SPACES_BUCKET, binder_key)
                                    if uploaded_pdf_key:
                                        binder_spaces_link = get_spaces_public_url(uploaded_pdf_key)
                                    
                                    # Clean up the merged PDF
                                    try:
                                        os.remove(merged_path)
                                    except Exception as del_e:
                                        print(f"[ERROR] Removing merged PDF: {del_e}")

                            # rename notes if final found
                            final_notes_path = os.path.join(NOTES_FOLDER, f"{cid}hasFinalReport.txt")
                            try:
                                os.rename(notes_file_path, final_notes_path)
                                notes_file_path = final_notes_path
                                print(f"[DEBUG] Renamed notes file to {notes_file_path}")
                            except Exception as rename_e:
                                print(f"[ERROR] Renaming notes file for {cid}: {rename_e}")

                            # re-upload notes
                            final_notes_key = f"notes/{cid}hasFinalReport.txt"
                            uploaded_notes_key = upload_file_to_spaces(notes_file_path, SPACES_BUCKET, final_notes_key)
                            if uploaded_notes_key:
                                notes_spaces_link = get_spaces_public_url(uploaded_notes_key)

                            # remove final PDF
                            try:
                                os.remove(final_pdf_path)
                                print(f"[DEBUG] Deleted final PDF for Claim {cid}")
                            except Exception as del_e:
                                print(f"[ERROR] Deleting final PDF: {del_e}")
                        else:
                            print(f"[ERROR] Final Report download failed for Claim {cid}")
                    except TimeoutException:
                        print(f"[DEBUG] No 'Final Report' found for {cid}")

                except (TimeoutException, NoSuchElementException) as e:
                    print(f"[ERROR] Could not load files for {cid}, skipping. Error: {e}")
                    driver.close()
                    driver.switch_to.window(original_tab)
                    continue

                # Close new tab
                driver.close()
                driver.switch_to.window(original_tab)

                # Insert into DB only if we have notes & binder
                if notes_spaces_link and binder_spaces_link:
                    store_in_db(cid, notes_spaces_link, binder_spaces_link)
                else:
                    print(f"[DEBUG] Missing either notes or binder for {cid}, skipping DB insert.")

            except Exception as row_e:
                #print(f"[ERROR] Unexpected row-level error for claim: {row_e}")
                continue

        # Finished processing rows on current page; attempt next page
        print("[DEBUG] Finished processing all rows on this page.")
        try:
            # Adjust this if your pagination link text is different
            next_button = driver.find_element(By.LINK_TEXT, "Next »")
            next_button.click()
            time.sleep(3)  # wait for the page to load
        except NoSuchElementException:
            print("[DEBUG] No more pages found. Exiting loop.")
            break

except Exception as e:
    print(f"[FATAL] Top-level error: {e}")

finally:
    driver.quit()
    print("[DEBUG] Script finished!")

    # Close DB connection
    db_cursor.close()
    db_connection.close()
