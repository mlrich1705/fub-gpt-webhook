from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ✅ Hardcoded for test
FUB_API_KEY = "fka_16VZis0qzdMZ42CVyzeXJsq5Zki2e3Nxnf"

# ✅ TEST endpoint to verify connection with Follow Up Boss
@app.route("/test-fub")
def test_fub():
    headers = {
        "Authorization": f"Bearer {FUB_API_KEY}",  # Correct format
        "Accept": "application/json"
    }
    response = requests.get("https://api.followupboss.com/v1/users/me", headers=headers)
    print("FUB response:", response.status_code, response.text)
    return {
        "status": response.status_code,
        "data": response.json()
    }

# ✅ Basic health check
@app.route("/", methods=["GET"])
def health_check():
    return "FUB webhook is live", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
