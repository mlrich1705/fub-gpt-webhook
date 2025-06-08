from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth
import os

app = Flask(__name__)

# Replace this with your actual API key or set as environment variable
FUB_API_KEY = os.getenv("FUB_API_KEY", "your_fub_api_key_here")

@app.route("/", methods=["GET"])
def health_check():
    return "FUB webhook is live", 200

@app.route("/get_lead_history", methods=["POST"])
def get_lead_history():
    data = request.json
    lead_name = data.get("lead_name", "")
    lead_email = data.get("lead_email", "")
    lead_phone = data.get("lead_phone", "")

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
        if lead_name and lead.get("name", "").lower() == lead_name.lower():
            matched_lead = lead
            break
        if lead_email and lead.get("emails"):
            for email in lead["emails"]:
                if email["value"].lower() == lead_email.lower():
                    matched_lead = lead
                    break
        if lead_phone and lead.get("phones"):
            for phone in lead["phones"]:
                if ''.join(filter(str.isdigit, phone["value"])) == ''.join(filter(str.isdigit, lead_phone)):
                    matched_lead = lead
                    break
        if matched_lead:
            break

    if not matched_lead:
        return jsonify({"error": "Lead not found."}), 404

    lead_id = matched_lead["id"]
    timeline_resp = requests.get(
        f"https://api.followupboss.com/v1/people/{lead_id}/timeline",
        auth=HTTPBasicAuth(FUB_API_KEY, "")
    )

    timeline = timeline_resp.json()
    return jsonify({
        "status": 200,
        "data": {
            "lead": matched_lead,
            "timeline": timeline
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
