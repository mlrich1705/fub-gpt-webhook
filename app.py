from flask import Flask, request, jsonify
import requests
import base64

app = Flask(__name__)

# Hardcoded API key for testing (you can switch back to os.environ.get later)
FUB_API_KEY = "fka_16VZis0qzdMZ42CVyzeXJsq5Zki2e3Nxnf"

# Encode API key in Basic Auth format
basic_auth = base64.b64encode(f"{FUB_API_KEY}:".encode()).decode()

@app.route("/test-fub")
def test_fub():
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Accept": "application/json"
    }
    response = requests.get("https://api.followupboss.com/v1/users/me", headers=headers)
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
