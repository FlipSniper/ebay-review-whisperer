from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
import time
import csv
from TranslateFeedback import load_language

# -------- Setup Edge Options --------
edge_driver_path = r"C:/Users/Swank/Downloads/edgedriver_win64/msedgedriver.exe"

def create_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    service = Service(executable_path=edge_driver_path)
    return webdriver.Edge(service=service, options=options)

def handle_captcha_if_present(driver, url):
    time.sleep(2)
    if "captcha" in driver.current_url or "splashui" in driver.current_url:
        print("🧩 CAPTCHA detected. Relaunching browser in visible mode for manual solving...")
        driver.quit()
        driver = create_driver(headless=False)
        driver.get(url)
        while "captcha" in driver.current_url or "splashui" in driver.current_url:
            print("⏳ Waiting for CAPTCHA to be solved...")
            time.sleep(3)
        print("✅ CAPTCHA solved. Continuing...")
    return driver

def safe_get(driver, url, retries=3, wait=3):
    for attempt in range(retries):
        try:
            driver.get(url)
            driver = handle_captcha_if_present(driver, url)
            time.sleep(wait)
            if "about:blank" in driver.current_url:
                raise Exception("Blank page loaded")
            return driver
        except Exception as e:
            print(f"⚠️ Navigation attempt {attempt+1} failed: {e}")
            time.sleep(wait)
    print("❌ Failed to load page after retries.")
    driver.quit()
    exit()

def wait_for_feedback_rows():
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr[data-feedback-id]"))
    )

def scrape_feedback_table():
    for attempt in range(3):
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "tr[data-feedback-id]")
            if not rows:
                raise Exception("No feedback rows found")

            data = []
            for row in rows:
                # Extract comment
                comment_elem = row.find_element(By.CSS_SELECTOR, ".card__comment span[aria-label]")
                comment = (comment_elem.get_attribute("aria-label") or "").strip()

                # rating type via icon class
                rating_type = "Unknown"
                if row.find_elements(By.CSS_SELECTOR, "svg.icon--feedback-positive"):
                    rating_type = "Positive"
                elif row.find_elements(By.CSS_SELECTOR, "svg.icon--feedback-negative"):
                    rating_type = "Negative"
                elif row.find_elements(By.CSS_SELECTOR, "svg.icon--feedback-neutral"):
                    rating_type = "Neutral"


                # Extract date
                try:
                    date_elem = row.find_element(By.CSS_SELECTOR, "td span[aria-label*='Past']")
                    date_txt = date_elem.get_attribute("aria-label").strip()
                except NoSuchElementException:
                    date_txt = "Unknown"

                data.append({
                    "comment": comment,
                    "rating_type": rating_type,
                    "date": date_txt
                })
            return data
        except Exception as e:
            print(f"⚠️ Scraping attempt {attempt+1} failed: {e}")
            time.sleep(2)
    print("❌ Failed to scrape feedback after 3 attempts.")
    return []

def click_next_page(driver, retries=3):
    for attempt in range(retries):
        try:
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "next-page"))
            )
            if not next_btn.is_enabled():
                return False
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(3)
            wait_for_feedback_rows()
            return True
        except Exception as e:
            print(f"⚠️ Pagination attempt {attempt+1} failed: {e}")
            time.sleep(2)
    print("🚪 No more pages or failed to paginate.")
    return False

# -------- Start Script --------
driver = create_driver(headless=True)

# -------- Step 1: Go to product page --------
product_url = "https://www.ebay.com/itm/354393355064?_skw=iphone13&epid=7049287499&itmmeta=01K2WCSQJACMHT8PZFF8JM4DQY&hash=item52837d7338:g:DDcAAOSwEjhjcrCI&itmprp=enc%3AAQAKAAAAwFkggFvd1GGDu0w3yXCmi1f%2B%2FjHEMp5MNuP%2BXQLXcy%2BXSK80Qfxwxi8g%2BTS9Ak4m8uhjQxggaOgPEWSwFA3zvifDh%2FVHOT7hDE8g6Jbg7ZLXB9usTDS4hz0ep53px03l0O3ck8UtKQ6TrXOuEMJcByCyVpwRQRtn%2Fs28dC3GEOoISdHdcYF8x1u4kH%2FGHoss9XWCM3atpxLWNlzB45A1LIQpa%2FubmZVZuiyo4vTilE1zp3yCT%2Bkrafz7l7L6jCzMIw%3D%3D%7Ctkp%3ABlBMUJz65oyXZg"
driver = safe_get(driver, product_url)

# -------- Step 2: Try to find feedback profile URL --------
feedback_url = None
try:
    store_link = driver.find_element(By.XPATH, "//a[contains(@href, '/str/')]")
    store_url = store_link.get_attribute("href")
    username = store_url.split("/")[-1].split("?")[0]
    feedback_tab_url = f"https://www.ebay.com/str/{username}?_tab=feedback"
    driver = safe_get(driver, feedback_tab_url)

    feedback_button = driver.find_element(By.XPATH, "//a[contains(@href, 'feedback_profile')]")
    feedback_url = feedback_button.get_attribute("href")
except Exception as e:
    try:
        feedback_button = driver.find_element(By.XPATH, "//a[contains(@href, '/fdbk/feedback_profile/')]")
        feedback_url = feedback_button.get_attribute("href")
    except:
        try:
            feedback_button = driver.find_element(By.XPATH, "//a[contains(@class, 'fdbk-detail-list___btn-container___btn')]")
            feedback_url = feedback_button.get_attribute("href")
        except Exception as final_e:
            print("❌ Couldn't find feedback link:", final_e)
            driver.quit()
            exit()

print("🔗 Feedback Profile URL:", feedback_url)

# -------- Step 3: Modify feedback URL to sort by recent --------
parsed = urlparse(feedback_url)
query_params = parse_qs(parsed.query)
query_params['filter'] = [quote('feedback_page: RECEIVED_AS_SELLER')]
query_params['sort'] = ['RecentV2']
for key in list(query_params):
    if key not in ['filter', 'sort']:
        del query_params[key]
feedback_url = urlunparse(parsed._replace(query=urlencode(query_params, doseq=True)))
driver = safe_get(driver, feedback_url)

# -------- Step 4: Click 200 items per page --------
try:
    wait_for_feedback_rows()
    button_200 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Click to show 200 feedback ratings per page']"))
    )
    driver.execute_script("arguments[0].click();", button_200)
    time.sleep(3)
    wait_for_feedback_rows()
except Exception as e:
    print("⚠️ Could not set 200 per page:", e)

# -------- Step 5: Scrape + Paginate --------
all_feedback = []
while len(all_feedback) < 400:
    page_data = scrape_feedback_table()
    all_feedback.extend(page_data)
    print(f"📦 Scraped {len(all_feedback)} feedback entries...")
    if not click_next_page(driver):
        break

# -------- Step 6: Save to test.csv without consecutive duplicates --------
print(all_feedback)
with open("test.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["comment", "rating_type", "date"])
    writer.writeheader()
    last_row = None
    unique_count = 0
    for entry in all_feedback:
        current_row = (entry["comment"], entry["rating_type"], entry["date"])
        if current_row != last_row:
            writer.writerow({
                "comment": entry["comment"],
                "rating_type": entry["rating_type"],
                "date": entry["date"]
            })
            last_row = current_row
            unique_count += 1

load_language('test.csv')

print(f"✅ Done! {unique_count} unique feedback entries saved to test.csv")
driver.quit()
