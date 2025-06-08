@app.route("/get_lead_history", methods=["POST"])
def get_lead_history():
    data = request.get_json()
    lead_name = data.get("lead_name")
    lead_email = data.get("lead_email")
    lead_phone = data.get("lead_phone")

    query = lead_name or lead_email or lead_phone
    if not query:
        return jsonify({"error": "You must provide a name, email, or phone"}), 400

    auth = HTTPBasicAuth(FUB_API_KEY, "")
    headers = {"Accept": "application/json"}
    search_resp = requests.get(
        "https://api.followupboss.com/v1/people",
        headers=headers,
        auth=auth,
        params={"q": query}
    )

    leads = search_resp.json().get("people", [])
    if not leads:
        return jsonify({"error": "Lead not found"}), 404

    matched_lead = leads[0]
    lead_id = matched_lead.get("id")

    timeline_resp = requests.get(
        f"https://api.followupboss.com/v1/people/{lead_id}/timeline",
        headers=headers,
        auth=auth
    )

    events = timeline_resp.json().get("events", [])
    messages = []
    for e in events:
        if e["type"] in ["Email", "Call", "Note", "Text"]:
            messages.append({
                "type": e["type"],
                "date": e.get("dateCreated", ""),
                "body": e.get("body", "") or e.get("message", ""),
                "agent": e.get("userName", "")
            })

    return jsonify({
        "lead_name": matched_lead.get("name"),
        "lead_id": lead_id,
        "messages": messages
    })
