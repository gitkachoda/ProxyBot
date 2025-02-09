import os
import time
import threading
import logging
import requests
import telebot
from flask import Flask, jsonify
from bs4 import BeautifulSoup

# ✅ Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server_logs.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ✅ Load environment variables for Render
TOKEN = os.getenv("BOT_TOKEN", "7607265539:AAHE0oHuCeHHDoOmbk5ULER7HRyH5HyZd-s")
CHAT_ID = int(os.getenv("CHAT_ID", "1289304344"))
PORT = int(os.getenv("PORT", 5000))

bot = telebot.TeleBot(TOKEN)
proxy_checking_active = False
proxy_thread = None

# ✅ Flask Server Setup
app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"status": "Bot is running!", "proxy_checking": proxy_checking_active})

@app.route("/status")
def status():
    return jsonify({"proxy_checking": proxy_checking_active})

@app.route("/keep_alive")
def keep_alive():
    logger.info("✅ Keep-alive ping received")
    return jsonify({"message": "Bot & Flask are active!"})

def keep_flask_alive():
    while True:
        try:
            requests.get(f"http://127.0.0.1:{PORT}/keep_alive")
        except Exception as e:
            logger.warning(f"⚠ Keep-alive failed: {e}")
        time.sleep(300)  # 5-minute interval

# ✅ Function to Scrape Proxies
def scrape_proxies():
    url = "https://www.sslproxies.org/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=60)
        if response.status_code != 200:
            logger.warning("⚠ Proxy scraping failed, retrying in 10 seconds...")
            time.sleep(10)
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        proxy_table = soup.find("table", class_="table")
        proxies = []

        if proxy_table:
            for row in proxy_table.find_all("tr")[1:]:
                columns = row.find_all("td")
                if len(columns) >= 2:
                    ip = columns[0].text.strip()
                    port = columns[1].text.strip()
                    proxies.append(f"{ip}:{port}")

        if not proxies:
            logger.warning("⚠ No proxies found, retrying...")
            return []

        logger.info(f"✅ Scraped {len(proxies)} proxies successfully.")
        return proxies

    except requests.RequestException as e:
        logger.error(f"❌ Proxy scraping error: {e}")
        return []

# ✅ Function to Check Proxy Latency
def check_proxy(proxy):
    test_url = "https://httpbin.org/ip"
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    try:
        start_time = time.time()
        response = requests.get(test_url, proxies=proxies, timeout=10)
        latency = int((time.time() - start_time) * 1000)

        if response.status_code == 200:
            return True, latency
    except requests.RequestException:
        return False, None

    return False, None

# ✅ Infinite Proxy Checker
def start_proxy_checker():
    global proxy_checking_active
    proxy_list = scrape_proxies()

    while proxy_checking_active:
        if not proxy_list:
            proxy_list = scrape_proxies()

        for proxy in proxy_list[:50]:
            if not proxy_checking_active:
                return  # Stop if command `/stop` is called

            is_working, latency = check_proxy(proxy)
            logger.info(f"🔄 Checking proxy: {proxy}")

            if is_working:
                bot.send_message(
                    CHAT_ID,
                    f"✅ *Working Proxy:* `{proxy}`\n⚡ Latency: {latency}ms",
                    parse_mode="Markdown"
                )
                logger.info(f"✅ Proxy Working: {proxy} | Latency: {latency}ms")
            else:
                logger.info(f"❌ Proxy Failed: {proxy}")

            time.sleep(1)

        logger.info("🕐 Waiting 5 minutes before next check...")
        time.sleep(300)  # 5-minute delay before next check

# ✅ Command to Start Proxy Checking
@bot.message_handler(commands=['startproxy'])
def start_proxy(message):
    global proxy_checking_active, proxy_thread

    if proxy_checking_active:
        bot.reply_to(message, "⚠ Proxy checking is already running!")
        return

    proxy_checking_active = True
    proxy_thread = threading.Thread(target=start_proxy_checker)
    proxy_thread.start()
    
    bot.reply_to(message, "✅ Proxy checking started!")

# ✅ Command to Stop Proxy Checking
@bot.message_handler(commands=['stop'])
def stop_proxy(message):
    global proxy_checking_active
    proxy_checking_active = False
    bot.reply_to(message, "❌ Proxy checking stopped!")

# ✅ Handle Invalid Commands
@bot.message_handler(func=lambda message: True)
def handle_invalid_command(message):
    bot.reply_to(message, "❓ Invalid command! Use:\n/startproxy - Start proxy checking\n/stop - Stop proxy checking")

# ✅ Telegram Bot Function
def run_bot():
    while True:
        try:
            print("\n🚀 Bot is running! Send /startproxy in Telegram to start proxy checking.")
            bot.polling()
        except Exception as e:
            print(f"\n⚠ Bot Crashed! Restarting in 5 seconds... Error: {e}")
            time.sleep(5)  # Restart after 5 seconds

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    threading.Thread(target=keep_flask_alive, daemon=True).start()

    while True:
        try:
            print("\n🚀 Starting Flask Server...")
            app.run(host="0.0.0.0", port=PORT)
        except Exception as e:
            print(f"\n⚠ Flask Crashed! Restarting in 5 seconds... Error: {e}")
            time.sleep(5)  # Restart after 5 seconds
