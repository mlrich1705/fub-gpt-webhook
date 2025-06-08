from flask import Flask, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

FUB_API_KEY = "fka_16VZis0qzdMZ42CVyzeXJsq5Zki2e3Nxnf"

@app.route("/test-fub")
def test_fub():
    url = "https://api.followupboss.com/v1/people"  # ✅ VALID endpoint
    headers = {
        "Accept": "application/json"
    }
    auth = HTTPBasicAuth(FUB_API_KEY, '')  # ✅ API key = username, password = blank

    response = requests.get(url, headers=headers, auth=auth)

    try:
        return jsonify({
            "status": response.status_code,
            "data": response.json()
        })
    except Exception as e:
        return jsonify({
            "status": response.status_code,
            "error": str(e),
            "raw": response.text
        })

@app.route("/", methods=["GET"])
def health_check():
    return "FUB webhook is live", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
