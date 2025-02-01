import requests
import re
import telebot
import time
import threading
from bs4 import BeautifulSoup

TOKEN = "7607265539:AAHE0oHuCeHHDoOmbk5ULER7HRyH5HyZd-s"
bot = telebot.TeleBot(TOKEN)

# Global variable to control proxy checking loop
proxy_checking_active = True

# ✅ Function to scrape proxies properly
def scrape_proxies():
    url = "https://www.sslproxies.org/"
    headers = {"User-Agent": "Mozilla/5.0"}

    while True:
        try:
            print("\n🔄 Fetching proxy list...")
            response = requests.get(url, headers=headers, timeout=60)

            if response.status_code != 200:
                print(f"❌ Failed to fetch proxies, Status Code: {response.status_code}")
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
                print("❌ No proxies found, retrying...")
                time.sleep(10)
                continue

            print(f"📌 Scraped {len(proxies)} proxies:", proxies[:5])  
            return proxies

        except requests.RequestException as e:
            print(f"⚠ Network error: {e}, retrying in 10 sec...")
            time.sleep(10)

# ✅ Function to check proxy latency (ms) & get location info
def check_proxy(proxy):
    test_url = "https://httpbin.org/ip"
    proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}

    try:
        start_time = time.time()  # ✅ Start ping timer
        response = requests.get(test_url, proxies=proxies, timeout=10)
        latency = int((time.time() - start_time) * 1000)  # ✅ Convert to milliseconds

        if response.status_code == 200:
            return True, latency
    except requests.RequestException:
        return False, None
    
    return False, None

# ✅ Function to get proxy location details (Country, ISP)
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

# ✅ Endless Loop to Keep Checking Proxies
def start_proxy_checker():
    global proxy_list, proxy_checking_active
    proxy_list = scrape_proxies()  

    while proxy_checking_active:
        if not proxy_list:
            print("\n♻️ Proxy list empty! Fetching new proxies...")
            proxy_list = scrape_proxies()

        for proxy in proxy_list[:25]:  
            if not proxy_checking_active:  
                print("\n❌ Stopping proxy checking as /stop was called.")
                return

            is_working, latency = check_proxy(proxy)

            if is_working:  
                country, region, isp = get_proxy_location(proxy)
                print(f"✅ Sending Working Proxy to Telegram: {proxy} ({country}, {region}, {isp}, {latency}ms)")
                
                # ✅ Send working proxy details to Telegram
                bot.send_message(
                    1289304344, 
                    f"🔥 *Working Proxy:* `{proxy}`\n📍 Country: {country}, {region}\n💻 ISP: {isp}\n⚡ Latency: {latency}ms\n(Copy & Use)"
                )

            time.sleep(1)  

        print("\n🔄 Refreshing proxy list in 5 minutes...\n")
        time.sleep(300)  

# ✅ Telegram command to get a working proxy
@bot.message_handler(commands=['getproxy'])
def send_proxy(message):
    bot.reply_to(message, "🔄 Scraping proxies, please wait...")

    proxies = scrape_proxies()

    if not proxies:
        bot.reply_to(message, "❌ No proxies found!")
        return

    bot.reply_to(message, f"🔍 Found {len(proxies)} proxies! Now testing...")

    working_proxies = []
    for proxy in proxies[:25]:  
        is_working, latency = check_proxy(proxy)
        if is_working:
            country, region, isp = get_proxy_location(proxy)
            working_proxies.append(f"{proxy} - {country}, {region} - {isp} - {latency}ms")
            bot.send_message(
                message.chat.id, 
                f"✅ *Proxy Working:* `{proxy}`\n📍 Country: {country}, {region}\n💻 ISP: {isp}\n⚡ Latency: {latency}ms\n(Copy & Use)"
            )

        time.sleep(1)  

    if working_proxies:
        bot.reply_to(message, "🔥 *Working Proxies:*\n" + "\n".join([f"`{p}`" for p in working_proxies]))
    else:
        bot.reply_to(message, "❌ No working proxies found!")

# ✅ Handle /stop command to stop proxy checking
@bot.message_handler(commands=['stop'])
def stop_proxy_checking(message):
    global proxy_checking_active
    proxy_checking_active = False
    bot.reply_to(message, "❌ Proxy checking stopped. No more proxies will be sent.")

# ✅ Handle any message and guide user
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.reply_to(message, "❓ Invalid command! Use:\n`/getproxy` to get working proxies.\n`/stop` to stop proxy checking.")

# ✅ Run Telegram bot and proxy checker in parallel
if __name__ == "__main__":
    print("\n📢 Type 'bot' to run Telegram bot, 'proxy' to run proxy checker, or 'both' for both.")
    user_input = input("Enter command: ").strip().lower()
    
    if user_input == "bot":
        print("\n🚀 Starting Telegram bot... Send /getproxy in Telegram!")
        bot.polling()
    elif user_input == "proxy":
        print("\n🔍 Starting Proxy Checker...")
        start_proxy_checker()
    elif user_input == "both":
        import threading
        print("\n🚀 Running Telegram bot & Proxy Checker in parallel!")
        t1 = threading.Thread(target=bot.polling)
        t2 = threading.Thread(target=start_proxy_checker)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    else:
        print("❌ Invalid input! Type 'bot', 'proxy', or 'both'.")
