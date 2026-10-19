from flask import Flask
import os, time, threading
from datetime import datetime

try:
    from quotexapi.stable_api import Quotex
    HAS_QUOTEX = True
    import_error = ""
except Exception as e:
    HAS_QUOTEX = False
    import_error = str(e)

app = Flask(__name__)
bot_log = []
is_running = True

EMAIL = os.environ.get("QUOTEX_EMAIL")
PASSWORD = os.environ.get("QUOTEX_PASS")

def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    full = f"{t} - {msg}"
    bot_log.append(full)
    print(full)
    if len(bot_log) > 100:
        bot_log.pop(0)

def check_candles(candles):
    red_count = 0
    for c in candles[-6:]:
        try:
            if c['close'] < c['open']:
                red_count += 1
        except:
            continue
    return red_count

def trading_loop():
    log("بوٹ شروع ہو رہا ہے...")
    if not EMAIL or not PASSWORD:
        log("❌ EMAIL / PASS نہیں ملا!")
        return
    if not HAS_QUOTEX:
        log(f"❌ Import Fail: {import_error}")
        return

    client = Quotex(email=EMAIL, password=PASSWORD)
    check, reason = client.connect()
    if not check:
        log(f"❌ لاگن فیل: {reason}")
        return
    
    log(f"✅ لاگن ہو گیا - Balance: {client.get_balance()}")
    assets = ["USDBRL_otc", "USDBRL", "USDPKR_otc"]
    
    while is_running:
        try:
            for asset in assets:
                candles = client.get_candles(asset, 60, 10, time.time())
                if not candles:
                    continue
                reds = check_candles(candles)
                log(f"{asset} - {reds} RED")
                if reds >= 6:
                    log(f"🔥 {asset} میں 6 RED! DOWN لگا رہا ہوں...")
                    status, buy_info = client.buy(1, asset, "put", 60)
                    log(f"{'✅ ٹریڈ لگی' if status else '❌ فیل'}: {buy_info}")
                    time.sleep(65)
            time.sleep(5)
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(10)

@app.route('/')
def home():
    logs = "<br>".join(reversed(bot_log[-50:]))
    color = "#22c55e" if HAS_QUOTEX else "#ef4444"
    return f"""<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body{{background:#0f172a;color:#fff;font-family:Arial;padding:15px;text-align:center}}
    .box{{background:#1e293b;padding:15px;border-radius:12px;max-width:600px;margin:auto;text-align:left}}
    .log{{background:#0b1120;padding:10px;border-radius:8px;height:500px;overflow:auto;font-size:13px}}</style></head>
    <body><h2>🤖 حماد آٹو بوٹ - REAL</h2>
    <p style="color:{color}">Email: {EMAIL} | Quotex: {'OK' if HAS_QUOTEX else 'Fail: '+import_error}</p>
    <div class="box"><div class="log">{logs}</div></div>
    <br><a href="/" style="color:#38bdf8">Refresh</a></body></html>"""

threading.Thread(target=trading_loop, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)