from flask import Flask
import os, time, threading, asyncio
from datetime import datetime
import httpx

# ===== FINAL FIX - reason_phrase + Cloudflare 403 =====
try:
    if not hasattr(httpx.Response, "reason_phrase"):
        httpx.Response.reason_phrase = property(lambda self: "OK")
    import pyquotex
    base_path = os.path.dirname(pyquotex.__file__)
    for r, d, f in os.walk(base_path):
        for file in f:
            if file.endswith(".py"):
                fp = os.path.join(r, file)
                try:
                    content = open(fp, 'r', encoding='utf-8', errors='ignore').read()
                    changed = False
                    if 'reason_phrase' in content:
                        content = content.replace('reason_phrase', 'reason')
                        changed = True
                    if 'quotex.com' in content:
                        content = content.replace('quotex.com', 'qxbroker.com')
                        changed = True
                    if changed:
                        open(fp, 'w', encoding='utf-8').write(content)
                except: pass
except Exception as e:
    print(f"Patch info: {e}")
# =====================================================

from pyquotex.stable_api import Quotex

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
    if len(bot_log) > 100: bot_log.pop(0)

def check_candles(candles):
    red_count = 0
    for c in candles[-6:]:
        try:
            if isinstance(c, dict) and c.get('close', 0) < c.get('open', 0): red_count += 1
            elif isinstance(c, (list, tuple)) and len(c) > 4 and c[4] < c[1]: red_count += 1
        except: continue
    return red_count

async def trading_loop_async():
    log("بوٹ شروع ہو رہا ہے...")
    if not EMAIL or not PASSWORD:
        log("❌ EMAIL / PASS Render > Environment me set karo!")
        return
    client = Quotex(email=EMAIL, password=PASSWORD)
    try:
        check, reason = await client.connect()
        if not check:
            log(f"❌ لاگن فیل: {reason}")
            log("10 min baad retry karunga (Cloudflare block)")
            await asyncio.sleep(600) # 10 min wait for Cloudflare
            return await trading_loop_async()
        balance = await client.get_balance()
        log(f"✅ لاگن ہو گیا - Balance: {balance}")
        assets = ["USDBRL_otc", "USDBRL", "USDPKR_otc"]
        while is_running:
            for asset in assets:
                try:
                    candles = await client.get_candles(asset, 60, 10, time.time())
                    if not candles: continue
                    reds = check_candles(candles)
                    log(f"{asset} - {reds} RED")
                    if reds >= 6:
                        log(f"🔥 {asset} میں 6 RED! DOWN لگا رہا ہوں...")
                        status, buy_info = await client.buy(1, asset, "put", 60)
                        log(f"{'✅ ٹریڈ لگی' if status else '❌ فیل'}: {buy_info}")
                        await asyncio.sleep(65)
                except Exception as e:
                    log(f"{asset} Error: {e}")
            await asyncio.sleep(5)
    except Exception as e:
        log(f"Main Error: {e}")

def trading_loop(): asyncio.run(trading_loop_async())

@app.route('/')
def home():
    logs = "<br>".join(reversed(bot_log[-50:]))
    return f"""<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body{{background:#0f172a;color:#fff;font-family:Arial;padding:15px;text-align:center}}
    .box{{background:#1e293b;padding:15px;border-radius:12px;max-width:600px;margin:auto;text-align:left}}
    .log{{background:#0b1120;padding:10px;border-radius:8px;height:500px;overflow:auto;font-size:13px}}</style></head>
    <body><h2>🤖 حماد آٹو بوٹ - REAL</h2><p style="color:#22c55e">Email: {EMAIL}</p>
    <p>USDBRL + USDPKR | 6 RED -> DOWN AUTO TRADE</p>
    <div class="box"><b>لائیو لاگ:</b><br><br><div class="log">{logs}</div></div><br><a href="/" style="color:#38bdf8">Refresh</a></body></html>"""

threading.Thread(target=trading_loop, daemon=True).start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))