from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
FUB_API_KEY = os.environ.get("FUB_API_KEY")
print("API key found:", bool(FUB_API_KEY))

@app.route("/get_lead_history", methods=["POST"])
def get_lead_history():
    data = request.get_json()
    lead_name = data.get("lead_name")
    lead_email = data.get("lead_email")
    lead_phone = data.get("lead_phone")

    search_query = lead_name or lead_email or lead_phone

    search_resp = requests.get(
        "https://api.followupboss.com/v1/people",
        headers={"Authorization": f"Bearer {FUB_API_KEY}"},
        params={"q": search_query}
    )

    leads = search_resp.json().get("people", [])
    print("Lead search results:")
    for lead in leads:
        print(f"- {lead.get('name')} (ID: {lead.get('id')})")
        print(f"  Emails: {lead.get('emails')}")
        print(f"  Phones: {lead.get('phones')}")

    if not leads:
        return jsonify({"error": "Lead not found"}), 404

    matched_lead = None
    for lead in leads:
        if lead_name and lead.get("name", "").lower() == lead_name.lower():
            matched_lead = lead
            break
        if lead_email and lead.get("emails"):
            for e in lead.get("emails"):
                if e.lower() == lead_email.lower():
                    matched_lead = lead
                    break
        if lead_phone and lead.get("phones"):
            clean_requested = ''.join(filter(str.isdigit, lead_phone))
            for stored_phone in lead.get("phones"):
                clean_stored = ''.join(filter(str.isdigit, stored_phone))
                if clean_requested == clean_stored:
                    matched_lead = lead
                    break
        if matched_lead:
            break

    if not matched_lead:
        return jsonify({"error": "Exact lead match not found"}), 404

    lead_id = matched_lead["id"]

    # Step 2: Get timeline
    timeline_resp = requests.get(
        f"https://api.followupboss.com/v1/people/{lead_id}/timeline",
        headers={"Authorization": f"Bearer {FUB_API_KEY}"}
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
