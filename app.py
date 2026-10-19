from flask import Flask
import os, time, threading
from datetime import datetime

# Quotex API
try:
    from quotexapi.stable_api import Quotex
    HAS_QUOTEX = True
except:
    HAS_QUOTEX = False

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
    # آخری 6 کینڈل چیک کریں RED ہیں یا نہیں
    red_count = 0
    for c in candles[-6:]:
        if c['close'] < c['open']: # RED
            red_count += 1
    return red_count

def trading_loop():
    log("بوٹ شروع ہو رہا ہے...")
    if not EMAIL or not PASSWORD:
        log("❌ EMAIL / PASS نہیں ملا! Environment میں ڈالیں")
        return
    
    if not HAS_QUOTEX:
        log("❌ quotexapi install نہیں ہوئی")
        return

    client = Quotex(email=EMAIL, password=PASSWORD)
    check, reason = client.connect()
    if not check:
        log(f"❌ لاگن فیل: {reason}")
        return
    
    log("✅ Quotex میں لاگن ہو گیا - Balance: " + str(client.get_balance()))
    log("USDBRL اور USDPKR چیک ہو رہے ہیں...")

    assets = ["USDBRL", "USDBRL_otc", "USDPKR", "USDPKR_otc"]
    
    while is_running:
        try:
            for asset in assets:
                candles = client.get_candles(asset, 60, 10, time.time()) # 1 min candles
                if not candles:
                    continue
                
                reds = check_candles(candles)
                log(f"{asset} - آخری 6 میں {reds} RED")

                if reds >= 6:
                    log(f"🔥 {asset} میں 6 RED ملی! DOWN ٹریڈ لگا رہا ہوں...")
                    # 1 ڈالر کی DOWN ٹریڈ 1 منٹ کے لیے
                    status, buy_info = client.buy(1, asset, "put", 60)
                    if status:
                        log(f"✅ ٹریڈ لگ گئی: {asset} DOWN - ID: {buy_info.get('id')}")
                    else:
                        log(f"❌ ٹریڈ فیل: {buy_info}")
                    time.sleep(65) # ایک ٹریڈ کے بعد 1 منٹ انتظار
            time.sleep(5)
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(10)

@app.route('/')
def home():
    logs = "<br>".join(reversed(bot_log[-50:]))
    status_color = "#22c55e" if EMAIL else "#ef4444"
    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body{{background:#0f172a;color:#fff;font-family:Arial;padding:15px;text-align:center}}
    .box{{background:#1e293b;padding:15px;border-radius:12px;max-width:600px;margin:auto;text-align:left}}
    .log{{background:#0b1120;padding:10px;border-radius:8px;height:500px;overflow:auto;font-size:13px;line-height:23px}}
    </style></head><body>
    <h2>🤖 حماد آٹو بوٹ - REAL</h2>
    <p style="color:{status_color}">Email: {EMAIL if EMAIL else 'نہیں ملا'} | Quotex: {'OK' if HAS_QUOTEX else 'Fail'}</p>
    <p>USDBRL + USDPKR | 6 RED -> DOWN AUTO TRADE</p>
    <div class="box"><b>لائیو لاگ:</b><br><br><div class="log">{logs}</div></div>
    <br><a href="/" style="color:#38bdf8">Refresh</a></body></html>
    """

threading.Thread(target=trading_loop, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)