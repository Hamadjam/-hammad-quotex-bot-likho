from flask import Flask
import os, time, threading, asyncio
from datetime import datetime
import httpx

# ===== FIX only reason_phrase =====
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
                    txt = open(fp, 'r', encoding='utf-8', errors='ignore').read()
                    if 'reason_phrase' in txt:
                        txt = txt.replace('reason_phrase', 'reason')
                        open(fp, 'w', encoding='utf-8').write(txt)
                except: pass
except: pass
# ===================================

from pyquotex.stable_api import Quotex
app = Flask(__name__)
bot_log = []
is_running = True
EMAIL = os.environ.get("QUOTEX_EMAIL")
PASSWORD = os.environ.get("QUOTEX_PASS")

def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    bot_log.append(f"{t} - {msg}")
    print(f"{t} - {msg}")

async def trading_loop_async():
    log("بوٹ شروع ہو رہا ہے...")
    if not EMAIL or not PASSWORD:
        log("❌ EMAIL / PASS nahi mila")
        return
    client = Quotex(email=EMAIL, password=PASSWORD)
    try:
        check, reason = await client.connect()
        if not check:
            log(f"❌ لاگن فیل: {reason}")
            log("Cloudflare ne IP block kiya hai, 15 min baad retry...")
            await asyncio.sleep(900)
            return await trading_loop_async()
        balance = await client.get_balance()
        log(f"✅ لاگن ہو گیا - Balance: {balance}")
        assets = ["USDBRL_otc", "USDBRL", "USDPKR_otc"]
        while is_running:
            for asset in assets:
                try:
                    candles = await client.get_candles(asset, 60, 10, time.time())
                    if not candles: continue
                    reds = sum(1 for c in candles[-6:] if (c.get('close',0) < c.get('open',0) if isinstance(c,dict) else c[4] < c[1] if len(c)>4 else False))
                    log(f"{asset} - {reds} RED")
                    if reds >= 6:
                        log(f"🔥 {asset} 6 RED -> DOWN")
                        status, info = await client.buy(1, asset, "put", 60)
                        log(f"{'✅ ٹریڈ لگی' if status else '❌ فیل'}: {info}")
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
    return f"<html><body style='background:#0f172a;color:#fff;font-family:Arial;padding:15px;text-align:center'><h2>🤖 حماد آٹو بوٹ - REAL</h2><p style='color:#22c55e'>Email: {EMAIL}</p><div style='background:#1e293b;padding:15px;border-radius:12px;max-width:600px;margin:auto;text-align:left'><div style='background:#0b1120;padding:10px;border-radius:8px;height:500px;overflow:auto;font-size:13px'>{logs}</div></div></body></html>"

threading.Thread(target=trading_loop, daemon=True).start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))