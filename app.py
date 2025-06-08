from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# 🔐 Use your API key here directly for now
FUB_API_KEY = "fka_16VZis0qzdMZ42CVyzeXJsq5Zki2e3Nxnf"

# ✅ Basic Auth setup
AUTH = HTTPBasicAuth(FUB_API_KEY, '')
HEADERS = {
    "Accept": "application/json"
}

@app.route("/test-fub")
def test_fub():
    response = requests.get("https://api.followupboss.com/v1/people", headers=HEADERS, auth=AUTH)
    return jsonify({
        "status": response.status_code,
        "data": response.json()
    })

@app.route("/get_lead_history", methods=["POST"])
def get_lead_history():
    data = request.get_json()
    lead_name = data.get("lead_name")
    lead_email = data.get("lead_email")
    lead_phone = data.get("lead_phone")

    search_query = lead_name or lead_email or lead_phone
    if not search_query:
        return jsonify({"error": "No search parameter provided"}), 400

    search_resp = requests.get(
        "https://api.followupboss.com/v1/people",
        headers=HEADERS,
        auth=AUTH,
        params={"q": search_query}
    )

    leads = search_resp.json().get("people", [])
    if not leads:
        return jsonify({"error": "Lead not found"}), 404

    matched_lead = leads[0]  # Simplified matching for now
    lead_id = matched_lead["id"]

    timeline_resp = requests.get(
        f"https://api.followupboss.com/v1/people/{lead_id}/timeline",
        headers=HEADERS,
        auth=AUTH
    )

    timeline = timeline_resp.json().get("events", [])
    messages = []
    for event in timeline:
        if event["type"] in ["Email", "Call", "Note", "Text"]:
            messages.append({
                "type": event["type"],
                "date": event["dateCreated"],
                "body": event.get("body", event.get("message", "")),
                "agent": event.get("userName", "")
            })

    return jsonify({
        "lead_name": matched_lead.get("name"),
        "lead_id": lead_id,
        "messages": messages
    })

@app.route("/", methods=["GET"])
def health_check():
    return "FUB webhook is live", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
