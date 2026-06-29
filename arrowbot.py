import requests
import time
from datetime import datetime
from flask import Flask
from threading import Thread
import sys

# Force all prints to appear immediately
def logger(msg):
    print(msg, flush=True)

# --- DUMMY WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Arrowbot is alive!"

def run_server():
    app.run(host="0.0.0.0", port=8080)

# Start server in background
Thread(target=run_server, daemon=True).start()

# --- BOT LOGIC ---
WEBHOOK_URL = "https://discord.com/api/webhooks/1521106196235554826/-m_0CVrCoteTMLyQoXncf0g0ITLv6FIAkvCgsOV1frGvOKKQ-85_ExF75sYWrerwySZc"
seen_bets = set()
HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'content-type': 'application/json',
    'origin': 'https://specialbets.arrowbet.co.uk',
    'partner-id': '18770617',
    'platform-id': '1',
    'referer': 'https://specialbets.arrowbet.co.uk/',
    'rgs-token': '4cf8f2bf74d92ae86a1be4e6e29cb',
    'user-agent': 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36',
    'x-api-key': 'ZL85d6rP15qbjbBI0I4ySo0hFG6aF41C'
}

def check_for_new_bets():
    logger(f"[{datetime.now().strftime('%H:%M:%S')}] Querying Arrowbet...")
    try:
        response = requests.get("https://poolmasters-api.arrowbet.co.uk/api/SpecialBet/GetSpecialBetOffers", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            offers = data.get("data", [])
            if not offers:
                logger(" -> Connection successful, no bets found.")
                return
            # ... (the rest of your loop logic remains the same)
            logger(f" -> Checked {len(offers)} items.")
        else:
            logger(f" -> Error {response.status_code}")
    except Exception as e:
        logger(f" -> Error: {e}")

logger("Starting Live Arrowbot...")
while True:
    check_for_new_bets()
    time.sleep(60)
