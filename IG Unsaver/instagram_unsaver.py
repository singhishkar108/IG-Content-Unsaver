import time
import random
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

# --- FAST & SAFE SETTINGS ---
ITEMS_PER_BATCH = 20        # Unsave 20 items rapidly
BATCH_PAUSE_SEC = 15       # Pause 15 seconds between batches to avoid API blocks
MAX_UNSAVES_THIS_RUN = 1000  # Total limit per session

# Instagram's Base64 alphabet for shortcodes
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

def shortcode_to_media_id(shortcode):
    """
    Converts an Instagram shortcode (e.g., 'DaPHXMZDUlI') 
    directly into its numeric Media ID offline.
    """
    media_id = 0
    for letter in shortcode:
        media_id = (media_id * 64) + ALPHABET.index(letter)
    return str(media_id)

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Selenium 4.6+ handles ChromeDriver downloading natively:
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1280, 900)
    return driver

def unsave_post_via_fetch(driver, media_id):
    """
    Sends direct unsave API fetch request using logged-in session cookies and CSRF token.
    """
    js_script = """
    var mediaId = arguments[0];
    var callback = arguments[1];

    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }

    var csrftoken = getCookie('csrftoken');

    fetch('/api/v1/web/save/' + mediaId + '/unsave/', {
        method: 'POST',
        headers: {
            'X-CsrfToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('HTTP status ' + response.status);
    })
    .then(data => callback({success: true, data: data}))
    .catch(err => callback({success: false, error: err.toString()}));
    """
    try:
        result = driver.execute_async_script(js_script, media_id)
        return result.get('success', False)
    except Exception:
        return False

def main():
    driver = setup_driver()
    driver.set_script_timeout(10)
    
    print("Navigating to Instagram...")
    driver.get("https://www.instagram.com/")
    print("\n[ACTION REQUIRED] Log into Instagram in the Chrome window that popped up.")
    input("Once you are logged in and on your homepage, press ENTER in this terminal to start...")

    driver.get(f"https://www.instagram.com/{username}/saved/all-posts/")
    print("\nNavigated to Saved Posts. Starting high-speed unsaver in 5 seconds...")
    time.sleep(5)

    processed_shortcodes = set()
    unsaved_count = 0

    try:
        while unsaved_count < MAX_UNSAVES_THIS_RUN:
            # Collect visible post shortcodes from links on grid
            links = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/') or contains(@href, '/reel/')]")
            current_batch_shortcodes = []

            for link in links:
                href = link.get_attribute("href")
                match = re.search(r'/(?:p|reel)/([^/]+)/', href)
                if match:
                    shortcode = match.group(1)
                    if shortcode not in processed_shortcodes:
                        current_batch_shortcodes.append(shortcode)
                        processed_shortcodes.add(shortcode)

            if not current_batch_shortcodes:
                print("No new posts visible. Scrolling down to load more...")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                continue

            print(f"\nFound {len(current_batch_shortcodes)} new posts. Unsaving batch...")

            for shortcode in current_batch_shortcodes:
                if unsaved_count >= MAX_UNSAVES_THIS_RUN:
                    break

                # Step 1: Convert shortcode to numeric Media ID instantly offline
                media_id = shortcode_to_media_id(shortcode)
                
                # Step 2: Unsave directly via background API call
                success = unsave_post_via_fetch(driver, media_id)
                if success:
                    unsaved_count += 1
                    print(f"[{unsaved_count}/{MAX_UNSAVES_THIS_RUN}] FAST UNSAVED: {shortcode} (ID: {media_id})")
                else:
                    print(f"[FAILED] Could not unsave shortcode {shortcode}")

                # Micro pause (0.15s = ~6-7 items per second)
                time.sleep(0.15)

                # Batch safety pause
                if unsaved_count > 0 and unsaved_count % ITEMS_PER_BATCH == 0:
                    print(f"\n--- Batch reached ({ITEMS_PER_BATCH} unsaved). Pausing {BATCH_PAUSE_SEC}s to respect API limits... ---\n")
                    time.sleep(BATCH_PAUSE_SEC)

            # Scroll down to fetch next set of thumbnails
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)

    except KeyboardInterrupt:
        print("\nScript stopped by user.")
    finally:
        print(f"\nSession complete. Total unsaved: {unsaved_count}")
        driver.quit()

if __name__ == "__main__":
    main()