# import time
# import random
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

# # --- SAFETY SETTINGS ---
# MIN_DELAY = 0.1           # Minimum delay between clicks (seconds)
# MAX_DELAY = 0.3           # Maximum delay between clicks (seconds)
# BATCH_SIZE = 20           # Pause after N actions
# BATCH_PAUSE_MIN = 60      # Min pause duration (seconds)
# BATCH_PAUSE_MAX = 120     # Max pause duration (seconds)
# MAX_UNSAVES_THIS_RUN = 200 # Limit per session

# def setup_driver():
#     options = webdriver.ChromeOptions()
#     options.add_argument("--disable-notifications")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#     driver.set_window_size(1280, 900)
#     return driver

# def find_remove_svg(driver):
#     """
#     Locates the actual SVG / title node for 'Remove' inside the post modal.
#     """
#     xpaths = [
#         "//section//svg[@aria-label='Remove']",
#         "//section//svg[./title[text()='Remove']]",
#         "//*[local-name()='svg' and (@aria-label='Remove' or ./*[local-name()='title' and text()='Remove'])]"
#     ]
#     for xpath in xpaths:
#         try:
#             elements = driver.find_elements(By.XPATH, xpath)
#             for el in elements:
#                 if el.is_displayed():
#                     return el
#         except Exception:
#             continue
#     return None

# def force_react_click(driver, element):
#     """
#     Dispatches full MouseEvents to ensure React triggers the state change.
#     """
#     script = """
#     var target = arguments[0];
#     var events = ['mousedown', 'mouseup', 'click'];
#     events.forEach(function(eventType) {
#         var event = new MouseEvent(eventType, {
#             view: window,
#             bubbles: true,
#             cancelable: true
#         });
#         target.dispatchEvent(event);
#     });
#     """
#     driver.execute_script(script, element)

# def is_unsaved(driver):
#     """
#     Checks if the button label changed from 'Remove' to 'Save'.
#     """
#     save_xpaths = [
#         "//section//svg[@aria-label='Save']",
#         "//section//svg[./title[text()='Save']]",
#         "//*[local-name()='svg' and (@aria-label='Save' or ./*[local-name()='title' and text()='Save'])]"
#     ]
#     for xpath in save_xpaths:
#         try:
#             elements = driver.find_elements(By.XPATH, xpath)
#             if any(el.is_displayed() for el in elements):
#                 return True
#         except Exception:
#             continue
#     return False

# def close_modal(driver):
#     """Safely closes post/reel modal using ESC key."""
#     try:
#         webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
#         time.sleep(0.2)
#     except Exception:
#         pass

# def main():
#     driver = setup_driver()
    
#     print("Navigating to Instagram...")
#     driver.get("https://www.instagram.com/")
#     print("\n[ACTION REQUIRED] Log into Instagram in the Chrome window that popped up.")
#     input("Once you are logged in and on your homepage, press ENTER in this terminal to start...")

#     # Redirect to saved posts
#     driver.get(f"https://www.instagram.com/{username}/saved/all-posts/")
#     print("\nNavigated to Saved Posts. Starting in 5 seconds...")
#     time.sleep(5)

#     unsaved_count = 0
#     current_index = 0

#     try:
#         while unsaved_count < MAX_UNSAVES_THIS_RUN:
#             posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/') or contains(@href, '/reel/')]")

#             if current_index >= len(posts):
#                 print("Reached end of visible items. Scrolling down...")
#                 driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 time.sleep(0.1)
#                 posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/') or contains(@href, '/reel/')]")
#                 if current_index >= len(posts):
#                     print("No new posts loaded. Ending run.")
#                     break

#             post = posts[current_index]
#             try:
#                 # Open modal by clicking thumbnail link
#                 driver.execute_script("arguments[0].click();", post)
#                 time.sleep(0.1)

#                 # Find the target SVG icon
#                 remove_icon = find_remove_svg(driver)

#                 if remove_icon:
#                     # Dispatch full click events directly to the SVG element
#                     force_react_click(driver, remove_icon)
#                     time.sleep(0.1)

#                     # Verify that state changed to 'Save'
#                     if is_unsaved(driver):
#                         unsaved_count += 1
#                         print(f"[{unsaved_count}/{MAX_UNSAVES_THIS_RUN}] SUCCESS: Unsaved Item #{current_index + 1}.")
#                     else:
#                         # Fallback: click parent div directly
#                         parent_div = remove_icon.find_element(By.XPATH, "./ancestor::div[@role='button'][1]")
#                         force_react_click(driver, parent_div)
#                         time.sleep(0.1)
                        
#                         if is_unsaved(driver):
#                             unsaved_count += 1
#                             print(f"[{unsaved_count}/{MAX_UNSAVES_THIS_RUN}] SUCCESS: Unsaved Item #{current_index + 1} (via parent).")
#                         else:
#                             print(f"[FAILED] Unsave click did not change button state for Item #{current_index + 1}.")
#                 else:
#                     print(f"[SKIPPED] Could not find 'Remove' icon on Item #{current_index + 1}.")

#                 close_modal(driver)

#             except Exception as e:
#                 print(f"Error processing item #{current_index + 1}: {e}")
#                 close_modal(driver)

#             current_index += 1

#             # Inter-item delay
#             delay = random.uniform(MIN_DELAY, MAX_DELAY)
#             time.sleep(delay)

#             # Batch pause
#             if unsaved_count > 0 and unsaved_count % BATCH_SIZE == 0:
#                 batch_pause = random.uniform(BATCH_PAUSE_MIN, BATCH_PAUSE_MAX)
#                 print(f"\n--- Batch pause ({BATCH_SIZE} unsaved). Pausing for {batch_pause / 60:.1f} min... ---\n")
#                 time.sleep(batch_pause)

#     except KeyboardInterrupt:
#         print("\nScript stopped by user.")
#     finally:
#         print(f"\nSession complete. Total unsaved: {unsaved_count}")
#         driver.quit()

# if __name__ == "__main__":
#     main()

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

    username = input("Enter your Instagram username: ")
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