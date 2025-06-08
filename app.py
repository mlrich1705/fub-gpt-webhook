from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import os

app = Flask(__name__)

# Permanent FUB API Key
FUB_API_KEY = os.getenv("FUB_API_KEY", "fka_16VZis0qzdMZ42CVyzeXJsq5Zki2e3Nxnf")


@app.route("/", methods=["GET"])
def health_check():
    return "FUB webhook is live", 200


@app.route("/test-fub", methods=["GET"])
def test_fub():
    url = "https://api.followupboss.com/v1/people"
    headers = {
        "Accept": "application/json"
    }
    auth = HTTPBasicAuth(FUB_API_KEY, '')

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


@app.route("/get_lead_history", methods=["POST"])
def get_lead_history():
    try:
        body = request.json
        query = body.get("name", "").strip()
        if not query:
            return jsonify({"error": "Missing name in request body"}), 400

        print(f"📡 Attempting to hit FUB /people endpoint with query: {query}")
        url = f"https://api.followupboss.com/v1/people?query={query}"
        headers = {"Accept": "application/json"}
        auth = HTTPBasicAuth(FUB_API_KEY, '')

        response = requests.get(url, headers=headers, auth=auth)

        print("Lead search results:")
        return jsonify({
            "status": response.status_code,
            "data": response.json()
        })
    except Exception as e:
        return jsonify({
            "status": 500,
            "error": str(e)
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
