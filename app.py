from flask import Flask
import threading, time, asyncio
from datetime import datetime

# ====== FIX FOR RENDER ERROR ======
import httpx
# reason_phrase کا Error ختم کرنے کے لیے
try:
    if not hasattr(httpx.Response, 'reason_phrase'):
        httpx.Response.reason_phrase = property(lambda self: "OK")
except:
    pass
# ===================================

from pyquotex import Quotex

app = Flask(__name__)
bot_log = []

EMAIL = "hamadjamal640@gmail.com"
PASSWORD = "Hammad@123"

def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    full = f"{t} - {msg}"
    bot_log.append(full)
    print(full)
    if len(bot_log) > 100:
        bot_log.pop(0)

async def trading_main():
    while True:
        try:
            log("بوٹ شروع ہو رہا ہے...")
            client = Quotex(email=EMAIL, password=PASSWORD)
            check, reason = await client.connect()
            if not check:
                log(f"Login Fail: {reason} - 2 min baad retry")
                await asyncio.sleep(120)
                continue
            
            log("✅ LOGIN HO GAYA - REAL ACCOUNT")
            bal = await client.get_balance()
            log(f"Balance: {bal}")

            while True:
                # USDBRL + USDPKR check
                for asset in ["USDBRL_otc", "USDPKR_otc"]:
                    try:
                        candles = await client.get_candles(asset, 60, 10, time.time())
                        if candles and len(candles) >= 6:
                            reds = sum(1 for c in candles[-6:] if c['close'] < c['open'])
                            if reds >= 6:
                                log(f"🔥 {asset} par 6 RED! DOWN laga raha...")
                                status, info = await client.buy(1, asset, "put", 60)
                                log(f"Trade Result: {status} | {info}")
                                await asyncio.sleep(70)
                    except Exception as e:
                        log(f"Candle Error {asset}: {e}")
                await asyncio.sleep(5)

        except Exception as e:
            log(f"Main Error: {e}")
            await asyncio.sleep(30)

def run_loop():
    asyncio.run(trading_main())

@app.route('/')
def home():
    logs_html = "<br>".join(reversed(bot_log))
    return f"""
    <html><body style='background:#0a192f; color:white; font-family: sans-serif; padding:20px;'>
    <h1>🤖 hamad.bot - REAL</h1>
    <p style='color:lime'>Email: {EMAIL} | Quotex: OK</p>
    <p>USDBRL + USDPKR | 6 RED -> DOWN AUTO TRADE</p>
    <hr>
    <h3>لائیو لاگ:</h3>
    <div style='background:black; padding:15px; border-radius:10px; height:400px; overflow-y:scroll;'>{logs_html}</div>
    </body></html>
    """

# Start bot in background
threading.Thread(target=run_loop, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)