@app.route("/get_lead_history", methods=["POST"])
def get_lead_history():
    data = request.get_json()
    lead_name = (data.get("lead_name") or "").strip().lower()
    lead_email = (data.get("lead_email") or "").strip().lower()
    lead_phone = ''.join(filter(str.isdigit, data.get("lead_phone", "")))

    # Combine into a single query string
    search_query = lead_name or lead_email or lead_phone
    if not search_query:
        return jsonify({"error": "Please provide at least a name, email, or phone"}), 400

    # Search people
    search_resp = requests.get(
        "https://api.followupboss.com/v1/people",
        headers={"Authorization": f"Bearer {FUB_API_KEY}"},
        params={"q": search_query}
    )
    leads = search_resp.json().get("people", [])

    matched_lead = None
    for lead in leads:
        # Name match
        if lead_name and lead.get("name", "").strip().lower() == lead_name:
            matched_lead = lead
            break
        # Email match
        for email in lead.get("emails", []):
            if email.get("value", "").lower() == lead_email:
                matched_lead = lead
                break
        # Phone match
        for phone in lead.get("phones", []):
            stored_phone = ''.join(filter(str.isdigit, phone.get("value", "")))
            if stored_phone == lead_phone:
                matched_lead = lead
                break
        if matched_lead:
            break

    if not matched_lead:
        return jsonify({"error": "Exact lead match not found"}), 404

    # Get communication history
    lead_id = matched_lead["id"]
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
                "body": event.get("body") or event.get("message", ""),
                "agent": event.get("userName", "")
            })

    return jsonify({
        "lead_name": matched_lead.get("name"),
        "lead_id": lead_id,
        "messages": messages
    })
