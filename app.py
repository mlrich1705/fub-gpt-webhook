from flask import Flask, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Replace this with your actual API key
FUB_API_KEY = "fka_16VZis0qzdMZ42CVyzeXJsq5Zki2e3Nxnf"
AUTH = HTTPBasicAuth(FUB_API_KEY, '')
HEADERS = {"Accept": "application/json"}


@app.route("/get_lead_history", methods=["POST"])
def get_lead_history():
    data = request.get_json()
    lead_name = data.get("lead_name")
    lead_email = data.get("lead_email")
    lead_phone = data.get("lead_phone")

    if not (lead_name or lead_email or lead_phone):
        return jsonify({"error": "Must provide name, email, or phone"}), 400

    # Use FUB search endpoint
    query = lead_email or lead_phone or lead_name
    search_url = "https://api.followupboss.com/v1/people"
    search_resp = requests.get(search_url, headers=HEADERS, auth=AUTH, params={"q": query})

    if search_resp.status_code != 200:
        return jsonify({"error": "Search failed", "details": search_resp.text}), 500

    people = search_resp.json().get("people", [])
    matched = None

    for person in people:
        if lead_email:
            for e in person.get("emails", []):
                if e.get("value", "").lower() == lead_email.lower():
                    matched = person
                    break
        elif lead_phone:
            clean_input = ''.join(filter(str.isdigit, lead_phone))
            for p in person.get("phones", []):
                stored = ''.join(filter(str.isdigit, p.get("value", "")))
                if stored == clean_input:
                    matched = person
                    break
        elif lead_name and person.get("name", "").lower() == lead_name.lower():
            matched = person
        if matched:
            break

    if not matched:
        return jsonify({"error": "Lead not found"}), 404

    # Fetch timeline
    person_id = matched["id"]
    timeline_url = f"https://api.followupboss.com/v1/people/{person_id}/timeline"
    timeline_resp = requests.get(timeline_url, headers=HEADERS, auth=AUTH)

    if timeline_resp.status_code != 200:
        return jsonify({"error": "Failed to fetch timeline", "details": timeline_resp.text}), 500

    events = timeline_resp.json().get("events", [])
    messages = [
        {
            "type": e["type"],
            "date": e["dateCreated"],
            "body": e.get("body", e.get("message", "")),
            "agent": e.get("userName", "")
        }
        for e in events if e["type"] in ["Email", "Call", "Note", "Text"]
    ]

    return jsonify({
        "lead_id": person_id,
        "lead_name": matched.get("name"),
        "messages": messages
    })


@app.route("/", methods=["GET"])
def health_check():
    return "FUB webhook is live", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
