<<<<<<< HEAD
import requests
import time
import threading
import telebot
from bs4 import BeautifulSoup

TOKEN = "7607265539:AAHE0oHuCeHHDoOmbk5ULER7HRyH5HyZd-s"
CHAT_ID = 1289304344  # Apna chat ID daalo

proxy_checking_active = False  # Flag to control proxy checking
proxy_thread = None  # Background thread


# ✅ Function to scrape proxies properly
=======
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

@app.route("/start_proxy")
def start_proxy_api():
    start_proxy(None)
    return jsonify({"message": "✅ Proxy checking started!"})

@app.route("/stop_proxy")
def stop_proxy_api():
    stop_proxy(None)
    return jsonify({"message": "❌ Proxy checking stopped!"})

# ✅ Function to Scrape Proxies
>>>>>>> 92d9e2b (changes)
def scrape_proxies():
    url = "https://www.sslproxies.org/"
    headers = {"User-Agent": "Mozilla/5.0"}

<<<<<<< HEAD
    while True:
        try:
            response = requests.get(url, headers=headers, timeout=60)
            if response.status_code != 200:
                time.sleep(10)
                continue

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
                time.sleep(10)
                continue

            return proxies

        except requests.RequestException:
            time.sleep(10)


# ✅ Function to check proxy latency
=======
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
>>>>>>> 92d9e2b (changes)
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

<<<<<<< HEAD

# ✅ Function to get proxy location details
def get_proxy_location(proxy):
    try:
        ip = proxy.split(":")[0]
        url = f"http://ip-api.com/json/{ip}?fields=country,regionName,isp"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            country = data.get("country", "Unknown")
            region = data.get("regionName", "Unknown")
            isp = data.get("isp", "Unknown")
            return country, region, isp
    except:
        pass

    return "Unknown", "Unknown", "Unknown"


=======
>>>>>>> 92d9e2b (changes)
# ✅ Infinite Proxy Checker
def start_proxy_checker():
    global proxy_checking_active
    proxy_list = scrape_proxies()

    while proxy_checking_active:
        if not proxy_list:
            proxy_list = scrape_proxies()

<<<<<<< HEAD
        for proxy in proxy_list[:25]:
=======
        for proxy in proxy_list[:50]:
>>>>>>> 92d9e2b (changes)
            if not proxy_checking_active:
                return  # Stop if command `/stop` is called

            is_working, latency = check_proxy(proxy)
<<<<<<< HEAD
            if is_working:
                country, region, isp = get_proxy_location(proxy)
                bot.send_message(
                    CHAT_ID,
                    f"🔥 *Working Proxy:* `{proxy}`\n📍 Country: {country}, {region}\n💻 ISP: {isp}\n⚡ Latency: {latency}ms\n(Copy & Use)",
                    parse_mode="Markdown"
                )
            time.sleep(1)

        time.sleep(300)  # 5-minute delay before next check


=======
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

>>>>>>> 92d9e2b (changes)
# ✅ Command to Start Proxy Checking
def start_proxy(message):
    global proxy_checking_active, proxy_thread

    if proxy_checking_active:
        bot.reply_to(message, "⚠ Proxy checking is already running!")
        return

    proxy_checking_active = True
    proxy_thread = threading.Thread(target=start_proxy_checker)
    proxy_thread.start()
    
<<<<<<< HEAD
    bot.reply_to(message, "✅ Proxy checking started! Working proxies will be sent continuously.")

=======
    bot.reply_to(message, "✅ Proxy checking started!")
>>>>>>> 92d9e2b (changes)

# ✅ Command to Stop Proxy Checking
def stop_proxy(message):
    global proxy_checking_active
    proxy_checking_active = False
    bot.reply_to(message, "❌ Proxy checking stopped!")

<<<<<<< HEAD

# ✅ Command to Get Instant Proxy List
def send_proxy(message):
    bot.reply_to(message, "🔄 Scraping proxies, please wait...")
    proxies = scrape_proxies()

    if not proxies:
        bot.reply_to(message, "❌ No proxies found!")
        return

    bot.reply_to(message, f"🔍 Found {len(proxies)} proxies! Now testing...")

    working_proxies = []
    for proxy in proxies[:10]:
        is_working, latency = check_proxy(proxy)
        if is_working:
            country, region, isp = get_proxy_location(proxy)
            working_proxies.append(f"{proxy} - {country}, {region} - {isp} - {latency}ms")
            bot.send_message(
                message.chat.id,
                f"✅ *Proxy Working:* `{proxy}`\n📍 Country: {country}, {region}\n💻 ISP: {isp}\n⚡ Latency: {latency}ms",
                parse_mode="Markdown"
            )
        time.sleep(1)

    if working_proxies:
        bot.reply_to(message, "🔥 *Working Proxies:*\n" + "\n".join([f"`{p}`" for p in working_proxies]))
    else:
        bot.reply_to(message, "❌ No working proxies found!")


# ✅ Bot Runner with Auto-Restart
def run_bot():
    global bot
    while True:
        try:
            bot = telebot.TeleBot(TOKEN)

            # ✅ Commands Register
            bot.message_handler(commands=['startproxy'])(start_proxy)
            bot.message_handler(commands=['stop'])(stop_proxy)
            bot.message_handler(commands=['getproxy'])(send_proxy)

            # ✅ Handle Invalid Commands
            @bot.message_handler(func=lambda message: True)
            def handle_all_messages(message):
                bot.reply_to(message, "❓ Invalid command! Use:\n/startproxy - Start proxy checking\n/getproxy - Get instant proxies\n/stop - Stop proxy checking")

            print("\n🚀 Bot is running! Send /startproxy in Telegram to start proxy checking.")
            bot.polling()

        except Exception as e:
            print(f"\n⚠ Bot Crashed! Error: {e}")
            print("🔄 Restarting bot in 5 seconds...\n")
            time.sleep(5)  # ✅ Delay before restarting bot


# ✅ Start Bot in Auto-Restart Mode
if __name__ == "__main__":
    run_bot()
=======
# ✅ Telegram Bot Function
def run_bot():
    bot.message_handler(commands=['startproxy'])(start_proxy)
    bot.message_handler(commands=['stop'])(stop_proxy)

    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        bot.reply_to(message, "❓ Invalid command! Use:\n/startproxy - Start proxy checking\n/stop - Stop proxy checking")

    print("\n🚀 Bot is running! Send /startproxy in Telegram to start proxy checking.")
    bot.polling()

# ✅ Run Flask & Bot in Parallel
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)  # ❌ Debug Mode Hata Diya
>>>>>>> 92d9e2b (changes)
