import requests
import time
import os

GITHUB_RAW_URL = "https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/dev/README-Off-Season.md"
TELEGRAM_BOT_TOKEN = os.environ["7609886460:AAF4qjUEl2pLPT7jvw18zJ57vXYbAn0c24M"]
TELEGRAM_CHAT_ID = os.environ["7401872854"]
DATA_FILE = "last_snapshot.txt"
CHECK_INTERVAL_MINUTES = 1  # Check every minute

def fetch_markdown():
    return requests.get(GITHUB_RAW_URL).text

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def detect_new_lines(old, new):
    return list(set(new.splitlines()) - set(old.splitlines()))

def load_last_snapshot():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return f.read()
    return ""

def save_snapshot(data):
    with open(DATA_FILE, "w") as f:
        f.write(data)

print("📡 Job Watch Bot Running...")
while True:
    new_data = fetch_markdown()
    old_data = load_last_snapshot()
    new_lines = detect_new_lines(old_data, new_data)
    job_lines = [line for line in new_lines if "|" in line and "http" in line]

    if job_lines:
        message = "🚨 " + "\n".join(job_lines[:5])
        send_telegram_message(message)
        print("✅ Alert sent.")
        save_snapshot(new_data)
    else:
        print("🟢 No new postings.")

    time.sleep(CHECK_INTERVAL_MINUTES * 60)
