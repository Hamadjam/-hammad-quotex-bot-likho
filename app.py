from flask import Flask, jsonify, request
from flask_cors import CORS
from quotexapi.stable_api import Quotex
import time, os

app = Flask(__name__)
CORS(app)

EMAIL = os.getenv("QUOTEX_EMAIL", "hamadjamal640@gmail.com")
PASS = os.getenv("QUOTEX_PASS", "@Nimrahn1")

print(f"Connecting {EMAIL}...")
q = Quotex(EMAIL, PASS)
try:
    check, reason = q.connect()
    print("Connected:", check, reason)
    print("Balance:", q.get_balance())
except Exception as e:
    print("Error:", e)

@app.route("/")
def home():
    try:
        bal = q.get_balance()
    except:
        bal = "N/A"
    return jsonify({"status":"HAMAD BOT LIVE - 6 CONSECUTIVE RED -> 7th DOWN", "balance": bal})

@app.route("/candles/<pair>")
def get_candles(pair):
    try:
        candles_raw = q.get_candles(pair, 60, 15, time.time())
        data = []
        for c in candles_raw:
            data.append({"open": c["open"], "close": c["close"], "isRed": c["close"] < c["open"]})
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/trade", methods=["POST"])
def do_trade():
    body = request.json or {}
    pair = body.get("pair", "USDBRL_otc")
    isLive = body.get("isLive", False)
    amount = 1
    try:
        # CONSECUTIVE CHECK - GREEN aaya to 0
        candles_raw = q.get_candles(pair, 60, 10, time.time())
        closed = candles_raw[:-1]
        consec = 0
        for c in reversed(closed):
            if c["close"] < c["open"]:
                consec += 1
            else:
                break
        
        if consec < 6:
            return jsonify({"status": False, "info": f"Not 6 consecutive, only {consec} lagatar"})

        q.change_account("real" if isLive else "demo")
        time.sleep(0.5)
        status, info = q.buy(amount, pair, "put", 60)
        bal = q.get_balance()
        return jsonify({"status": status, "info": str(info), "balance": bal, "consec": consec})
    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)