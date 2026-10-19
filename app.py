from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/status')
def status():
    return jsonify({
        "status": "LIVE", 
        "bot": "hammad-quotex-bot",
        "strategy": "6 RED -> DOWN $1",
        "email": os.getenv("QUOTEX_EMAIL", "hamadjamal640@gmail.com")
    })

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)