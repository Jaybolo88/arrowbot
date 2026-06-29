import requests
import time
from datetime import datetime
from flask import Flask
from threading import Thread

# --- DUMMY WEB SERVER TO KEEP THE BOT AWAKE ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Arrowbot is alive and running!"

def run_server():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run_server)
    t.start()
# ----------------------------------------------

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

def send_discord_alert(bet, total_active):
    current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    
    content = (
        f"🏹 **1 new boost(s) on Arrowbet!**\n"
        f"• {bet['event_name']} — {bet['bet_description']}\n\n"
        f"https://www.arrowbet.co.uk/special-bets"
    )
    
    embed = {
        "color": 5763719,
        "title": f"🚨 {bet['event_name']}",
        "fields": [
            {"name": "📋 Bet", "value": bet['bet_description'], "inline": False},
            {"name": "✅ Selection", "value": bet['selection'], "inline": False},
            {"name": "📈 Odds", "value": bet['odds'], "inline": False},
            {"name": "💰 Stake", "value": bet['stake_limits'], "inline": False},
            {"name": "⏰ Expires", "value": bet['expires'], "inline": False}
        ],
        "footer": {
            "text": f"{total_active} total boosts active • {current_time}"
        }
    }
    
    payload = {
        "username": "Arrowbot",
        "content": content,
        "embeds": [embed]
    }
    
    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print(" -> [SUCCESS] Alert sent to Discord!")
    else:
        print(f" -> [ERROR] Failed to send alert to Discord: {response.status_code}")

def check_for_new_bets():
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] Querying Arrowbet live system...")
    
    api_url = "https://poolmasters-api.arrowbet.co.uk/api/SpecialBet/GetSpecialBetOffers"
    
    try:
        response = requests.get(api_url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            live_boosts = []
            
            offers_list = data.get("data", [])
            
            if not offers_list:
                print(" -> Connection successful, but no active special bets found in the data.")
                return

            for item in offers_list:
                event_name = item.get("name", "Special Boost")
                min_stake = item.get("minBetAmountLimit", 1)
                max_stake = item.get("maxBetAmountLimit", 2500)
                
                raw_date = item.get("endDate", "See Site")
                expires = raw_date.replace("T", ", ").replace("Z", "") if "T" in raw_date else raw_date
                
                matches = item.get("specialBetMatches", [])
                
                for match in matches:
                    if match.get("isCustomEvent"):
                        desc = match.get("eventName", "Special Bet")
                    else:
                        team1 = match.get("team1", "")
                        team2 = match.get("team2", "")
                        desc = f"{team1} vs {team2}" if team1 and team2 else match.get("marketName", "Match Result")
                    
                    selections = match.get("specialBetSelections", [])
                    
                    for sel in selections:
                        orig_odd = sel.get("originalOdd", 0)
                        boost_odd = sel.get("boostedOdd", 0)
                        
                        if len(selections) > 1 and boost_odd == 0:
                            continue
                        
                        if boost_odd > 0 and boost_odd != orig_odd:
                            odds_str = f"{orig_odd} -> {boost_odd}"
                        else:
                            odds_str = str(orig_odd)
                            
                        selection_name = sel.get("name", "Yes")
                        
                        bet_info = {
                            "id": str(sel.get("id", match.get("id"))),
                            "event_name": event_name,
                            "bet_description": desc,
                            "selection": selection_name,
                            "odds": odds_str,
                            "stake_limits": f"£{min_stake} - £{max_stake}",
                            "expires": expires
                        }
                        live_boosts.append(bet_info)
            
            for bet in live_boosts:
                bet_id = bet["id"]
                if bet_id not in seen_bets:
                    print(f" -> Found a BRAND NEW live boost: {bet['bet_description']}")
                    send_discord_alert(bet, len(live_boosts))
                    seen_bets.add(bet_id)
                else:
                    print(f" -> Boost already seen ({bet['bet_description']}). Skipping alert.")
                    
        else:
            print(f" -> Website connection error. Status code: {response.status_code}")
            
    except Exception as e:
        print(f" -> An unexpected error occurred while scraping: {e}")

if __name__ == "__main__":
    print("Starting Live Arrowbot... (Press Ctrl + C to stop)")
    keep_alive() # NEW: This launches the dummy website
    while True:
        check_for_new_bets()
        time.sleep(60)