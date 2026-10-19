from flask import Flask
import os, time, threading
from datetime import datetime

app = Flask(__name__)

bot_log = ["بوٹ تیار ہے... Live ہے"]
is_running = True

def bot_loop():
    global bot_log
    count = 0
    while is_running:
        count += 1
        msg = f"{datetime.now().strftime('%H:%M:%S')} - چیکنگ USDBRL/USDPKR - {count}"
        bot_log.append(msg)
        print(msg)
        if len(bot_log) > 40:
            bot_log.pop(0)
        time.sleep(5)

@app.route('/')
def home():
    logs = "<br>".join(reversed(bot_log[-30:]))
    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body{{background:#0f172a;color:#fff;font-family:Arial;padding:15px;text-align:center}}
    .box{{background:#1e293b;padding:15px;border-radius:12px;max-width:500px;margin:auto;text-align:left}}
    .log{{background:#0b1120;padding:10px;border-radius:8px;height:400px;overflow:auto;font-size:13px;line-height:22px}}
    .ok{{color:#22c55e}} .red{{color:#ef4444}}
    </style></head><body>
    <h2>🤖 حماد آٹو بوٹ</h2>
    <p class="ok">🟢 LIVE - Deploy کامیاب</p>
    <p>USDBRL + USDPKR | 6 RED -> DOWN Strategy</p>
    <div class="box">
    <b>لائیو لاگ:</b><br><br>
    <div class="log">{logs}</div>
    </div>
    <br><a href="/" style="color:#38bdf8">Refresh</a>
    </body></html>
    """

# Bot background me chalao
threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)