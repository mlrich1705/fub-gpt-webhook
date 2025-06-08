from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

FUB_API_KEY = "fka_16VZis0qzdMZ42CVyzeXJsq5Zki2e3Nxnf"

@app.route("/test-fub")
def test_fub():
    headers = {
        "Accept": "application/json"
    }
    auth = HTTPBasicAuth(FUB_API_KEY, '')  # API key as username, blank password
    response = requests.get("https://api.followupboss.com/v1/users/me", headers=headers, auth=auth)
    print("FUB response:", response.status_code, response.text)
    return {
        "status": response.status_code,
        "data": response.json()
    }

@app.route("/", methods=["GET"])
def health_check():
    return "FUB webhook is live", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
