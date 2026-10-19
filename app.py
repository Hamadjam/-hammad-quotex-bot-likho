from flask import Flask
from quotexapi.stable_api import Quotex
import os, time, threading
from datetime import datetime

app = Flask(__name__)

# پاسورڈ یہاں نہیں لکھنا، یہ Render سے آئے گا
EMAIL = os.environ.get("QUOTEX_EMAIL")
PASSWORD = os.environ.get("QUOTEX_PASSWORD")

ASSETS = ["USDBRL", "USDBRL_otc", "USDPKR", "USDPKR_otc"]

client = None
bot_log = ["بوٹ تیار ہے..."]
is_running = False

def get_red_count(asset):
    try:
        candles = client.get_candles(asset, 60, 10, time.time())
        if not candles:
            return 0
        count = 0
        for c in reversed(candles):
            if c['close'] < c['open']:
                count += 1
            else:
                break
        return count
    except:
        return 0

def bot_loop():
    global client, is_running, bot_log
    if not EMAIL or not PASSWORD:
        bot_log.append("ERROR: Render میں EMAIL / PASSWORD نہیں ملا")
        return

    client = Quotex(email=EMAIL, password=PASSWORD)
    check, reason = client.connect()
    if not check:
        bot_log.append(f"لاگ ان فیل: {reason}")
        return

    bot_log.append(f"لاگ ان کامیاب! بیلنس: {client.get_balance()}")
    is_running = True

    while is_running:
        for asset in ASSETS:
            reds = get_red_count(asset)
            bot_log.append(f"{datetime.now().strftime('%H:%M:%S')} - {asset} - {reds}/6 RED")
            if reds >= 6:
                bot_log.append(f">>> سگنل {asset} پر 6 RED - DOWN لگا رہا ہوں")
                status, info = client.buy(1, asset, "put", 60)
                bot_log.append(f"ٹریڈ {'کامیاب' if status else 'ناکام'}")
                time.sleep(70)
            if len(bot_log) > 30:
                bot_log.pop(0)
        time.sleep(3)

@app.route('/')
def home():
    logs = "<br>".join(bot_log[-25:])
    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body{{background:#0f172a;color:#fff;font-family:Arial;padding:20px;text-align:center}}
    .box{{background:#1e293b;padding:20px;border-radius:12px;max-width:500px;margin:auto;text-align:left}}
    .log{{background:#0b1120;padding:10px;border-radius:8px;height:350px;overflow:auto;font-size:13px}}
    </style></head><body>
    <h2>🤖 حماد آٹو بوٹ</h2>
    <p>USDBRL + USDPKR | 6 RED -> DOWN</p>
    <div class="box">
    <b>اسٹیٹس:</b> {"🟢 چل رہا ہے" if is_running else "🔴 بند"}<br><br>
    <div class="log">{logs}</div>
    </div></body></html>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=port)