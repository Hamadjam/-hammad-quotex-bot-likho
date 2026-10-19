from flask import Flask, jsonify
from flask_cors import CORS
import os
app = Flask(__name__)
CORS(app)
@app.route('/')
def home():
    return jsonify({"status": "LIVE", "bot": "hammad-bot", "strategy": "6 RED -> DOWN"})
@app.route('/check')
def check():
    return jsonify({"live": True})
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)