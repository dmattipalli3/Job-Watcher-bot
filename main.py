import os
import time
import requests

# Debug: starting bot
print("🛠️ Starting bot...")

# Load environment variables
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
print("✅ Got bot token")

TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
print("✅ Got chat ID")

# Configuration
GITHUB_RAW_URL = "https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/dev/README-Off-Season.md"
DATA_FILE = "last_snapshot.txt"
CHECK_INTERVAL_MINUTES = 1

# --- Functions ---
def fetch_markdown():
    print("🔍 Fetching markdown from GitHub...")
    response = requests.get(GITHUB_RAW_URL)
    print("✅ Fetched markdown; status code:", response.status_code)
    return response.text

def send_telegram_message(message):
    print("📤 Sending Telegram message:")
    print(message)
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    print("✅ Telegram response status code:", response.status_code)

def detect_new_lines(old, new):
    old_lines = set(old.splitlines())
    new_lines = set(new.splitlines())
    result = list(new_lines - old_lines)
    print("🔍 Detected", len(result), "new lines")
    return result

def load_last_snapshot():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = f.read()
            print("✅ Loaded last snapshot from file")
            return data
    else:
        print("ℹ️ No snapshot file found, starting fresh")
        return ""

def save_snapshot(data):
    with open(DATA_FILE, "w") as f:
        f.write(data)
    print("✅ Snapshot saved to file")

# 🚨 One-time manual test to send the current last job from GitHub
print("📄 Fetching latest job for manual test...")
full_text = fetch_markdown()
all_job_lines = [line for line in full_text.splitlines() if "|" in line and "http" in line]

if all_job_lines:
    latest_job = all_job_lines[0]
    test_message = "🚨 Manual test — latest job from GitHub:\n" + latest_job
    send_telegram_message(test_message)
    print("✅ Sent latest job via Telegram:")
    print(latest_job)
else:
    print("⚠️ No job lines found in GitHub file.")

# 🔁 Start main loop
print("🚀 Entering main loop...")
while True:
    print("🔁 Looping...")
    new_data = fetch_markdown()
    old_data = load_last_snapshot()

    # Skip alerts on first run
    if old_data == "":
        print("📂 First-time run: saving current data without sending alerts")
        save_snapshot(new_data)
        time.sleep(CHECK_INTERVAL_MINUTES * 60)
        continue

    new_lines = detect_new_lines(old_data, new_data)
    job_lines = [line for line in new_lines if "|" in line and "http" in line]
    print("🔍 Found", len(job_lines), "job lines")

    if job_lines:
        message = "🚨 " + "\n".join(job_lines[:5])
        send_telegram_message(message)
        print("✅ Alert sent.")
        save_snapshot(new_data)
    else:
        print("🟢 No new postings.")

    print("⏱ Sleeping for", CHECK_INTERVAL_MINUTES, "minute(s)...")
    time.sleep(CHECK_INTERVAL_MINUTES * 60)

