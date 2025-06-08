from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# 🔐 Replace this key later with os.environ.get(...) for production
FUB_API_KEY = "fka_16VZis0qzdMZ42CVyzeXJsq5Zki2e3Nxnf"

@app.route("/test-fub")
def test_fub():
    url = "https://api.followupboss.com/v1/people"
    headers = {"Accept": "application/json"}
    auth = HTTPBasicAuth(FUB_API_KEY, "")
    response = requests.get(url, headers=headers, auth=auth)
    try:
        return jsonify({"status": response.status_code, "data": response.json()})
    except Exception as e:
        return jsonify({"status": response.status_code, "error": str(e), "raw": response.text})

@app.route("/get_lead_history", methods=["POST"])
def get_lead_history():
    data = request.get_json()
    lead_name = data.get("lead_name")
    lead_email = data.get("lead_email")
    lead_phone = data.get("lead_phone")

    search_query = lead_name or lead_email or lead_phone
    print("📡 Attempting to hit FUB /people endpoint with query:", search_query)

    search_resp = requests.get(
        "https://api.followupboss.com/v1/people",
        auth=HTTPBasicAuth(FUB_API_KEY, ""),
        params={"q": search_query}
    )

    leads = search_resp.json().get("people", [])
    print("Lead search results:", leads)

    matched_lead = None
    for lead in leads:
        # match by name
        if lead_name and lead.get("name", "").lower() == lead_name.lower():
            matched_lead = lead
            break
        # match by email
        if lead_email and lead.get("emails"):
            for email in lead["emails"]:
                if email["value"].lower() == lead_email.lower():
                    matched_lead = lead
                    break
        # match by phone
        if lead_phone and lead.get("phones"):
            for phone in lead["phones"]:
                if ''.join(filter(str.isdigit, phone["value"])) == ''.join(filter(str.isdigit, lead_phone)):
                    matched_lead = lead
                    break
        if matched_lead:
            break

    if not matched_lead:
        return jsonify({"error": "Lead not found"}), 404

    lead_id = matched_lead["id"]
    timeline_url = f"https://api.followupboss.com/v1/people/{lead_id}/timeline"
    timeline_resp = requests.get(timeline_url, auth=HTTPBasicAuth(FUB_API_KEY, ""))
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
