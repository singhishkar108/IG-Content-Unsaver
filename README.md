<div align="center">

<h1 align="center">
  <img src="./assets/instagram.svg" width="32" alt="Instagram">
  Instagram Content Unsaver
  <img src="./assets/python.svg" width="32" alt="Python">
</h1>

</div>

---

## 📑Table of Contents

🧭 1. [**Introduction**](#-1-introduction)<br>
🆚 2. [**Script Versions (V1 vs. V2)**](#-2-script-versions-v1-vs-v2)<br>
💻 3. [**Setting Up the Project Locally**](#-3-setting-up-the-project-locally)<br>
📖 4. [**User Guide**](#-4-user-guide)<br>
🏗️ 5. [**Architecture**](#️-5-architecture)<br>
⚠️ 6. [**Disclaimer**](#️-5-architecture)<br>
👨‍💻 7. [**Author and Contributions**](#-7-author-and-contributions)<br>
⚖️ 8. [**MIT License**](#️-8-mit-license)<br>
❓ 9. [**Frequently Asked Questions (FAQ)**](#-9-frequently-asked-questions-faq)<br>

---

## 🧭 1. Introduction:

An automated, high-performance Python utility built with **Selenium** for bulk-managing and clearing saved post collections on Instagram. Designed to bypass the manual friction of native interfaces, this repository offers both visual browser-driven automation and zero-network-overhead batch API execution.

### Overview

Instagram’s native application and web interface lack bulk-management tools for saved collections. Users who systematically bookmark posts, reels, or guides over extended periods eventually accumulate hundreds, or thousands of saved items without a native way to bulk-select or mass-unsave them. Manually removing items through the standard interface requires opening each post individually and clicking through modal overlays, making large-scale collection cleanup extremely tedious.

**Instagram Unsaver** resolves this bottleneck by automating the unsaving process inside an authentic browser session. Powered by Python and Selenium, it provides two distinct execution strategies depending on your speed requirements, collection size, and preference for visual inspection.

### Key Features

- **Dual Engine Architecture:** Choose between a DOM-simulated UI clicker (**V1**) and an ultra-fast background API interceptor (**V2**).
- **Offline Shortcode Resolution (V2):** Utilizes Base64 mathematical decoding to convert Instagram shortcodes (e.g., `DaPHXMZDUlI`) directly into internal numeric `Media ID`s offline, eliminating third-party metadata scrapers and extra network lookup requests.
- **Session-Authenticated Security:** Operates strictly within an active, human-authenticated Chrome session. It utilizes live cookies and CSRF tokens directly from your browser, eliminating the need to store passwords, API keys, or access tokens in plain text.
- **Adaptive Rate Limiting & Safety:** Built-in micro-delays, batch limits, and scheduled cooldown pauses help prevent trigger-happy execution and mitigate Instagram rate-limit blocks (`429 Too Many Requests`), as well as prevent your account from being temporarily suspended.
- **Infinite Scroll Harvesting:** Dynamically scrolls the saved post feed to load and queue new items on the fly without interrupting ongoing cleanup operations.

---

## 🆚 2. Script Versions (V1 vs. V2)

To accommodate different collection sizes, user preferences, and execution requirements, this repository provides two distinct script architectures. Both versions utilize the same authenticated Chrome browser session but differ fundamental in how they interact with Instagram's web application.

### Version 1: DOM Interaction Engine (`instagram_unsaver_v1.py`)

#### Overview

Version 1 is a **UI-driven browser automation script**. It simulates authentic human navigation by interacting directly with the document object model (DOM) of Instagram's web page. It opens each post visually, inspects button states, and triggers UI events.

#### Execution Pipeline

1. **Grid Extraction:** Identifies post and reel thumbnail elements (`<a>` tags) rendered on the active `/saved/all-posts/` page.
2. **Modal Invocation:** Dispatches a JavaScript click to open the individual post in a modal overlay.
3. **Element Resolution:** Uses dynamic XPath expressions to locate the active "Remove" SVG bookmark icon or its parent container.
4. **State Dispatch:** Dispatches explicit MouseEvents (`mousedown`, `mouseup`, `click`) directly to the SVG element to trigger React state changes.
5. **Verification & Fallback:** Scans the DOM to ensure the button label transitions from `Remove` to `Save`. If unverified, it attempts a fallback click on the parent element container (`div[role='button']`).
6. **Modal Dismissal:** Emulates pressing the `ESC` key via Selenium `ActionChains` to close the modal and resume grid traversal.

#### Pros & Cons

- **Pros:**
- Highly visual and easy to audit, you can watch the script open and unsave posts in real time.
- Resilient against internal API structural changes since it relies on front-end UI components.

- **Cons:**
- High execution overhead due to image/video rendering in post modals.
- Significantly slower throughput (~1 unsave every 3–5 seconds).
- Susceptible to DOM timing issues or temporary layout shifts if network latency causes delays in modal loading.

### Version 2: Session-Authenticated API Interceptor (`instagram_unsaver.py`)

#### Overview

Version 2 is an **ultra-fast background network automation script**. It completely bypasses front-end UI rendering and modal dialogs. Instead, it extracts link parameters directly from the grid, decodes post identifiers offline, and issues authenticated background POST requests to Instagram's internal API endpoints.

#### Execution Pipeline

1. **Shortcode Harvesting:** Extracts post shortcodes (e.g., `DaPHXMZDUlI` from `/p/DaPHXMZDUlI/`) directly from the visible thumbnail href attributes on the grid page.
2. **Offline Base64 Decoding:** Converts the shortcode string into Instagram’s internal 64-bit numeric `Media ID` locally using pure Base64 arithmetic (no external lookup requests required).
3. **Session Interception:** Extracts the live `X-CSRFToken` from the browser’s active cookie store.
4. **Direct API Dispatch:** Sends an asynchronous `fetch` request directly to Instagram's endpoint:
   `POST /api/v1/web/save/{media_id}/unsave/`
5. **Batching & Rate Control:** Executes requests in rapid bursts with micro-delays (~0.15s per request), enforcing a scheduled cooldown period (e.g., 15 seconds after every 20 unsaves) to avoid API rate limiting.

#### Key Technical Feature: Offline Shortcode Decoding

Instagram shortcodes are Base64-encoded representations of internal numeric database IDs. Rather than making network calls to fetch metadata, V2 decodes shortcodes offline using Instagram's character set (`A-Z`, `a-z`, `0-9`, `-`, `_`):

$$\text{Media ID} = \sum_{i=0}^{n-1} \left( \text{Index}(\text{shortcode}[i]) \times 64^{(n - 1 - i)} \right)$$

This allows the script to derive the target endpoint URL instantly with zero network lookup overhead.

#### Pros & Cons

- **Pros:**
- **Extreme Speed:** Capable of unsaving 6–10 posts per second (excluding safety cooldown pauses).
- **Minimal Overhead:** Eliminates modal rendering, media downloads, and UI state waiting.
- **Network Efficient:** Low bandwidth consumption.

- **Cons:**
- Low visual feedback (progress is monitored strictly via terminal logs).
- Relies on Instagram maintaining its internal `/api/v1/web/save/` endpoint structure.

### Technical Comparison Matrix

| Specification           | Version 1 (DOM Engine)                        | Version 2 (API Interceptor)                   |
| ----------------------- | --------------------------------------------- | --------------------------------------------- |
| **Primary Mechanism**   | Selenium DOM Clicks & Modals                  | Session-Authenticated `fetch()` Requests      |
| **Average Speed**       | ~12–20 items / minute                         | ~300–500 items / minute (unthrottled)         |
| **DOM Dependent**       | **Yes** (Requires visible modal & SVGs)       | **No** (Only requires grid `<a>` hrefs)       |
| **Network Overhead**    | High (Downloads full post media)              | Minimal (Lightweight JSON responses)          |
| **Session Safety**      | High (Resembles human mouse clicks)           | Moderate-High (Managed via batch pauses)      |
| **Verification Method** | DOM State Inspection (`Save` vs `Remove`)     | HTTP Response Codes (`200 OK` / JSON success) |
| **Best Suited For**     | Small collections (< 50 items), visual audits | Large collections (100+ items), mass cleanup  |

### Selecting the Right Version

- **Choose V1 if:** You are cleaning a small saved list, want to visually verify each item as it gets unsaved, or if Instagram changes its internal API endpoints.
- **Choose V2 if:** You have hundreds or thousands of saved posts to clear, want maximum speed, and prefer a silent, background operation.

---

## 💻 3. Setting Up the Project Locally

Follow the instructions below to configure your local development environment, install the required dependencies, and execute the scripts.

### 1. Prerequisites

Before setting up the project, ensure your system meets the following software requirements:

- **Python:** Version `3.8` or newer is required. You can verify your installation by running `python --version` in your terminal. (Download from [python.org](https://www.python.org/downloads/)).
- **Google Chrome:** A recent, stable version of the Google Chrome browser must be installed on your machine.
- **Package Manager:** Python’s package manager `pip` should be installed (it is typically bundled with standard Python installations).
- **Git (Optional):** Required only if you intend to clone the repository via the command line.

### 2. Downloading the Repository

You must first download the project files to your local machine. Choose **one** of the three methods below:

#### Method A: Command Line (Git Clone)

This is the recommended method for developers comfortable with the terminal.

1. Open your terminal or command prompt.
2. Navigate to the directory where you want to store the project (e.g., `cd Documents/Projects`).
3. Run the following command:

```bash
git clone https://github.com/your-username/IG-Content-Unsaver.git
```

4. Navigate into the newly created project folder:

```bash
cd ig-unsaver
```

#### Method B: GitHub Desktop

Ideal if you prefer a graphical interface for managing Git repositories.

1. Download and install [GitHub Desktop](https://desktop.github.com/).
2. Navigate to the main page of this repository on GitHub.
3. Click the green **Code** button and select **Open with GitHub Desktop**.
4. Follow the prompts in the GitHub Desktop application to select a local path and clone the repository.

#### Method C: Download ZIP

The simplest method if you do not want to use Git.

1. Navigate to the main page of this repository on GitHub.
2. Click the green **Code** button and select **Download ZIP**.
3. Locate the downloaded ZIP file on your computer and extract (unzip) it to your desired folder location.

### 3. Environment Setup & Installation

Once the project files are on your machine, you need to open the project and install the necessary Python dependencies.

#### 3.1: Open in Your IDE

Open the extracted or cloned `IG-Content-Unsaver` folder in your preferred Integrated Development Environment (IDE). **Visual Studio Code (VS Code)** is highly recommended.

- If using VS Code, you can simply open your terminal, navigate to the folder, and type:

```bash
code .
```

#### 3.2: Create a Virtual Environment (Recommended)

While optional, it is best practice to create an isolated Python virtual environment to prevent dependency conflicts with other projects on your machine.

1. Open a terminal directly within your IDE (or navigate to the project folder in your system terminal).

2. Create the virtual environment by running:

- **Windows:** `python -m venv venv`
- **macOS/Linux:** `python3 -m venv venv`

3. Activate the virtual environment:

- **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
- **Windows (Command Prompt):** `.\venv\Scripts\activate.bat`
- **macOS/Linux:** `source venv/bin/activate`

_(Note: You will know it is activated when you see `(venv)` appear at the start of your terminal prompt line)._

#### 3.3: Install Dependencies

With your terminal located in the root of the project folder (and your virtual environment activated, if you chose to use one), install the required packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This command will install `selenium` and any other required libraries necessary for the browser automation to function.

### 4. Running the Application

Before running the scripts, ensure you have updated the code with your specific Instagram username if you haven't already. (Locate the URL string in the script and replace the placeholder with your username).

Execute the script by running **one** of the following commands in your terminal, depending on which engine you wish to use:

- **To run the API Batch Engine (V2 - High Speed):**

```bash
python instagram_unsaver.py
```

- **To run the DOM Clicker Engine (V1 - Visual Interaction):**

```bash
python instagram_unsaver_v1.py
```

### 5. The Authentication Handshake

Upon executing either script, an automated instance of Google Chrome will launch.

1. **Do not close this browser window.**
2. The script will pause and prompt you via the terminal.
3. Manually log into your Instagram account inside the newly opened Chrome window.
4. Once you are fully logged in and can view your feed, return to your terminal and press **ENTER**.
5. The script will take over, navigate to your Saved Posts, and begin the automated unsaving process based on your chosen script version.

---

## 📖 4. User Guide

Configuring safety parameters, initiating execution, reading terminal output, and safely managing script execution.

### 1. Configuring Script Parameters

Both script versions feature configurable constants near the top of the file. You can customize these variables to suit your desired balance of speed and safety.

#### Configuration Variables

| Variable                         | Default Value | Description                                                                     |
| -------------------------------- | ------------- | ------------------------------------------------------------------------------- |
| `MAX_UNSAVES_THIS_RUN`           | `200`         | Hard cap on the total number of posts to unsave in a single execution session.  |
| `ITEMS_PER_BATCH` / `BATCH_SIZE` | `20`          | The number of consecutive unsaves before triggering a scheduled cooldown pause. |
| `BATCH_PAUSE_SEC` (V2)           | `15`          | Duration (in seconds) to pause between API batches.                             |
| `BATCH_PAUSE_MIN` / `MAX` (V1)   | `60` – `120`  | Minimum and maximum duration (in seconds) for batch pauses in UI mode.          |
| `MIN_DELAY` / `MAX_DELAY` (V1)   | `0.1` – `0.3` | Random interval range (in seconds) between individual click actions.            |

> **Recommended Practice:** For large accounts, keep `MAX_UNSAVES_THIS_RUN` around `200–300` items per session, and run the script once or twice per day to avoid triggering Instagram's rate limiters.

### 2. Step-by-Step Execution Workflow

#### 1: Set Your Instagram Username

Open your chosen script (`instagram_unsaver.py` or `instagram_unsaver_v1.py`) in your editor and ensure the target URL matches your Instagram username:

```python
# Replace with your actual Instagram handle
driver.get(f"https://www.instagram.com/{username}/saved/all-posts/")
```

#### 2: Launch the Script

Open your terminal inside the project directory and run your target engine:

```bash
# High-Speed API Engine (Recommended)
python instagram_unsaver.py

# DOM UI Engine
python instagram_unsaver_v1.py
```

#### 3: Complete the Authentication Handshake

1. A clean Chrome browser window will launch automatically and navigate to `[https://www.instagram.com/](https://www.instagram.com/)`.
2. Look at your terminal prompt:

```text
[ACTION REQUIRED] Log into Instagram in the Chrome window that popped up.
Once you are logged in and on your homepage, press ENTER in this terminal to start...
```

3. In the Chrome window, enter your Instagram credentials and complete any two-factor authentication (2FA) steps if prompted.
4. Once your home feed loads inside the browser, return to your terminal window and press **ENTER**.

#### 4: Automated Execution

The script will redirect the browser to your saved posts page (`/saved/all-posts/`), automatically scroll down to harvest thumbnail links, and begin unsaving items.

### 3. Monitoring Terminal Progress

As the script processes items, it logs real-time status updates directly to your terminal.

#### Example Terminal Output (V2 Engine)

```text
Navigating to Instagram...

[ACTION REQUIRED] Log into Instagram in the Chrome window that popped up.
Once you are logged in and on your homepage, press ENTER in this terminal to start...

Navigated to Saved Posts. Starting high-speed unsaver in 5 seconds...

Found 20 new posts. Unsaving batch...
[1/200] FAST UNSAVED: DaPHXMZDUlI (ID: 3559123456789012345)
[2/200] FAST UNSAVED: DaOKxAdNMWQ (ID: 3559123456789012346)
...
[20/200] FAST UNSAVED: DaLYuVWtRJp (ID: 3559123456789012364)

--- Batch reached (20 unsaved). Pausing 15s to respect API limits... ---

Reached end of visible items. Scrolling down to load more...
Found 20 new posts. Unsaving batch...
```

#### Log Status Definitions

- **`FAST UNSAVED` / `SUCCESS`:** The item was successfully removed from your saved list.
- **`--- Batch reached ... Pausing ---`:** The script has entered a safety cooldown pause to stay under rate limits.
- **`Reached end of visible items. Scrolling down...`:** The script reached the bottom of loaded grid thumbnails and dispatched a scroll command to trigger Instagram’s infinite scroll loader.
- **`[FAILED] / [SKIPPED]`:** An item was skipped or failed to unsave (typically occurs if a post was already deleted by the original poster).

### 4. Safely Interrupting or Stopping Execution

You can halt the execution at any point without corrupting your account or losing progress:

1. Click into your terminal window.
2. Press **`Ctrl + C`** (or `Cmd + C` on macOS).
3. The script will intercept the keyboard interrupt, output a final session summary, safely terminate the Selenium browser instance, and exit:

```text
^C
Script stopped by user.

Session complete. Total unsaved: 64
```

---

## 🏗️ 5. Architecture

The project is built on a **Hybrid Browser-Network Automation Pattern**. Instead of relying on full headless HTTP clients (which trigger anti-bot protections like Cloudflare or Instagram's IP blocks) or pure GUI automation (which is slow and fragile), it leverages a live, authenticated Chrome instance managed via Selenium WebDriver as a secure execution bridge.

### High-Level System Architecture

```text
  +------------------------------------------------------------------+
  |                           User Terminal                          |
  |             (Script Invocation & Logging Output)                 |
  +------------------------------------------------------------------+
                                   |
                                   v
  +------------------------------------------------------------------+
  |                      Python Control Layer                        |
  |  +----------------------------+  +----------------------------+  |
  |  |   V1: DOM Engine           |  |   V2: API Engine           |  |
  |  |   - UI Element Scraper     |  |   - Base64 Shortcode Dec.  |  |
  |  |   - MouseEvent Dispatcher  |  |   - Async Fetch Injector   |  |
  |  +----------------------------+  +----------------------------+  |
  |  +------------------------------------------------------------+  |
  |  |            Throttling & Batch Control Pipeline             |  |
  |  +------------------------------------------------------------+  |
  +------------------------------------------------------------------+
                                   |
                                   v
  +------------------------------------------------------------------+
  |                       Selenium WebDriver                         |
  |        (Manages Session Credentials, Cookies, and DOM)           |
  +------------------------------------------------------------------+
                                   |
                                   v
  +------------------------------------------------------------------+
  |                      Instagram Web Client                        |
  |    +-----------------------+      +---------------------------+  |
  |    |  DOM UI / Modals      |  OR  |  /api/v1/web/save/        |  |
  |    |  (Rendered Grid)      |      |  (Internal Endpoint)      |  |
  |    +-----------------------+      +---------------------------+  |
  +------------------------------------------------------------------+

```

### Core Architectural Components

#### 1. Session & Cookie Bridge (`setup_driver` & Authentication Handshake)

Rather than requiring stored plain-text passwords or external auth tokens, the script initializes a standard automated Chrome profile.

- **Authentication Storage:** Session state, local storage, and high-security session cookies (`sessionid`, `csrftoken`, `ds_user_id`) remain isolated within the browser instance memory.
- **CSRF Token Injection:** When V2 executes background requests, it extracts the live `csrftoken` dynamically from `document.cookie` inside the active browser context, ensuring valid request headers for all outgoing API calls.

#### 2. Grid Link Harvester

Both engines rely on a non-destructive grid-crawling strategy:

- Uses localized XPath expressions (`//a[contains(@href, '/p/') or contains(@href, '/reel/')]`) to extract visible post links.
- Utilizes regex shortcode parsing (`/(?:p|reel)/([^/]+)/`) to build a deduplicated set of target identifiers (`processed_shortcodes`).
- Triggers native window scroll events (`window.scrollTo(0, document.body.scrollHeight)`) to activate Instagram’s infinite scroll intersection observer when the visible DOM links are exhausted.

#### 3. Base64 Offline ID Encoder (V2 Core)

Instagram shortcodes are customized Base64 representations of internal integer primary keys. To avoid network overhead, V2 uses an offline mathematical transpiler:

- **Alphabet Mapping:** Instagram uses a custom 64-character lookup table:
  `A-Z`, `a-z`, `0-9`, `-`, `_`
- **Mathematical Transpilation:** Each shortcode character is converted to its positional base-10 value and shifted across a Base64 positional system to generate the 64-bit integer `Media ID`.

#### 4. Execution Engines

##### Engine A: DOM Event Dispatcher (V1)

- Bypasses standard Selenium `.click()` limitations on dynamic React virtual DOM elements by evaluating custom JavaScript synthetic `MouseEvent` sequences (`mousedown` $\rightarrow$ `mouseup` $\rightarrow$ `click`).
- Traverses the DOM tree to locate parent button containers (`div[role='button']`) if the primary SVG target state update fails.

##### Engine B: Asynchronous Network Injector (V2)

- Uses Selenium’s `execute_async_script` to inject native asynchronous `fetch()` requests directly into the running web page context.
- Transmits payload headers (`X-CsrfToken`, `X-Requested-With: XMLHttpRequest`) seamlessly via the browser's native network stack, preserving browser fingerprinting, TLS parameters, and HTTP/2 connections.

#### 5. Adaptive Throttling & Rate-Control Pipeline

To prevent account flagging and IP rate limits (`HTTP 429`), execution flows through a double-tier queue controller:

- **Micro-Throttling:** Implements configurable random jitter intervals between consecutive post actions to simulate human interaction latency.
- **Batch Cooldown Scheduler:** Tracks active state changes and forces full execution pauses after processing a set quota of items (`BATCH_SIZE` / `ITEMS_PER_BATCH`).

### Data Pipeline Workflow (V2 Batch Engine)

```text
[ Grid Link Harvester ]
       │  Extracts href "/p/DaPHXMZDUlI/"
       ▼
[ Shortcode Extractor ]
       │  Parses "DaPHXMZDUlI"
       ▼
[ Offline Base64 Decoders ]
       │  Converts string to Media ID: "3559123456789012345"
       ▼
[ Session Header Extractor ]
       │  Reads active 'csrftoken' from document.cookie
       ▼
[ Native Async Fetch Injection ]
       │  POST /api/v1/web/save/3559123456789012345/unsave/
       ▼
[ Throttling Controller ]
       │  Verifies response status (HTTP 200 OK)
       │  Increments counter & checks batch pause limit
       ▼
[ Terminal Output & Next Item ]

```

---

## ⚠️ 6. Disclaimer

### 1. Educational and Personal Use Only

This repository and its associated scripts are developed strictly for **educational purposes, technical research, and personal administrative utility**. The project serves as a practical demonstration of browser automation, web interaction models, and Base64 algorithm decoding in Python.

### 2. Terms of Service & Compliance

Automating actions on Instagram, including bulk operations, automated background requests, or session-assisted scraping, may violate [Instagram's Terms of Use](https://help.instagram.com/581066165581870) and [Community Guidelines](https://help.instagram.com/477434105621119). Automated activity can trigger Instagram's anti-bot mechanisms, resulting in temporary action blocks, rate limiting (`HTTP 429 Too Many Requests`), IP bans, or account suspension/termination.

### 3. Limitation of Liability ("Use at Your Own Risk")

**THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.**

By downloading, installing, or executing any script in this repository, you acknowledge and agree that:

- You are executing the software voluntarily and at your **own risk**.
- You are solely responsible for compliance with any applicable local laws and platform terms of service.
- The authors and maintainers of this project accept **no responsibility or liability** for any direct, indirect, incidental, or consequential damages resulting from the use or misuse of this code, including but not limited to:
- Temporary or permanent account bans, suspensions, or shadowbans.
- API action restrictions or rate limits applied to your Instagram account or IP address.
- Accidental or irreversible loss of saved posts, media collections, or personal account data.

### 4. Non-Affiliation Notice

This project is an independent open-source utility and is **not affiliated, associated, authorized, endorsed by, or in any way officially connected** with Instagram, Meta Platforms, Inc., or any of their subsidiaries or affiliates. All product and company names, trademarks, and registered trademarks belong to their respective owners.

---

## 👨‍💻 7. Author and Contributions

### Primary Developer:

- I, **_Ishkar Singh_**, am the sole developer and author of this project:
  Email (for feedback or concerns): **ishkar.singh.108@gmail.com**

### Reporting Issues:

- If you encounter any bugs, glitches, or unexpected behaviour, please open an Issue on the GitHub repository.
- Provide as much detail as possible, including:
  - Steps to reproduce the issue
  - Error messages (if any)
  - Screenshots or logs (if applicable)
  - Expected vs. actual behaviour
- Clear and descriptive reports help improve the project effectively.

### Proposing Enhancements:

- Suggestions for improvements or feature enhancements are encouraged.
- You may open a Discussion or submit an Issue describing the proposed change.
- All ideas will be reviewed and considered for future updates.

---

## ⚖️ 8. MIT License

**Copyright © 2026 Ishkar Singh**<br>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## ❓ 9. Frequently Asked Questions (FAQ)

### 1. Why does the script sometimes struggle or stall when scrolling down?

**A:** Instagram uses dynamic lazy-loading for its web grid. Occasionally, the DOM reaches the end of the currently rendered HTML elements before Instagram's background scripts finish fetching the next batch of items.

- **Fix/Workaround:** The script will automatically retry scrolling on its next loop. If it gets stuck for a prolonged period, simply switch to the opened Chrome window, scroll down manually once or twice to force Instagram to load new post thumbnails, and return to the terminal.

### 2. Why do a few specific posts fail to unsave or get skipped?

**A:** In a small percentage of cases, an individual post may fail to unsave due to:

1. **Deleted Media:** The original creator deleted the post or deactivated their account, leaving a "ghost" thumbnail in your saved list.
2. **Private Accounts:** The source account went private or blocked access.
3. **Network Jitter / API Response Drop:** A temporary micro-timeout occurred during the background fetch.

- **Fix/Workaround:** The script automatically logs these as `[FAILED]` or `[SKIPPED]` and continues with the queue so the entire batch isn't halted. Running the script a second time after a short break will usually clean up any remaining items that were skipped due to temporary network timeouts.

### 3. How many posts can I safely unsave in one day?

**A:** To keep your account well within safe operational limits, it is recommended to run **no more than 200–400 unsaves per day**, split into batches with cooldown pauses.

### 4. What should I do if I receive an `HTTP 429 (Too Many Requests)` error?

**A:** An `HTTP 429` error means Instagram's rate limiters have detected rapid API activity and temporarily throttled your IP or session.

1. Stop the script (`Ctrl + C`).
2. Increase the `BATCH_PAUSE_SEC` setting in your script (e.g., from `15` to `30` or `60` seconds).
3. Wait **1 to 2 hours** before running the script again.

### 5. Can I run this script headlessly (without opening a Chrome window)?

**A:** While Selenium supports headless mode, running Instagram in headless Chrome significantly increases the likelihood of triggering anti-bot challenges or CAPTCHAs. Running a visible Chrome session with manual login remains the safest and most reliable method.
