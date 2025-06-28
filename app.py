from flask import Flask, request, jsonify
from datetime import datetime
import json
import uuid
from utils import load_events, save_events, send_email


app = Flask(__name__)
DATA_FILE = "events.json"
events = load_events(DATA_FILE)


# Create Event
@app.route("/events", methods=["POST"])
def create_event():
    data = request.json
    event_id = str(uuid.uuid4())
    event = {
        "id": event_id,
        "title": data["title"],
        "description": data["description"],
        "start_time": data["start_time"],
        "end_time": data["end_time"]
    }
    events.append(event)
    save_events(events, DATA_FILE)
    return jsonify({"message": "Event created", "event": event}), 201


# Get All Events
@app.route("/events", methods=["GET"])
def expand_recurring_events():
    expanded = []
    now = datetime.now()
    for event in events:
        expanded.append(event)
        if event.get("recurrence"):
            for i in range(1, 4):
                e = event.copy()
                start = datetime.fromisoformat(event["start_time"])
                end = datetime.fromisoformat(event["end_time"])
                if event["recurrence"] == "daily":
                    delta = timedelta(days=i)
                elif event["recurrence"] == "weekly":
                    delta = timedelta(weeks=i)
                elif event["recurrence"] == "monthly":
                    delta = timedelta(days=30 * i)
                else:
                    continue
                e["start_time"] = (start + delta).isoformat()
                e["end_time"] = (end + delta).isoformat()
                expanded.append(e)
    return expanded

@app.route("/events", methods=["GET"])
def get_events():
    sorted_events = sorted(expand_recurring_events(), key=lambda e: e["start_time"])
    return jsonify(sorted_events)

@app.route("/search", methods=["GET"])
def search_events():
    query = request.args.get("q", "").lower()
    result = [e for e in events if query in e["title"].lower() or query in e["description"].lower()]
    return jsonify(result)


# Update Event
@app.route("/events/<event_id>", methods=["PUT"])
def update_event(event_id):
    data = request.json
    for event in events:
        if event["id"] == event_id:
            event.update(data)
            save_events(events, DATA_FILE)
            return jsonify({"message": "Event updated", "event": event})
    return jsonify({"error": "Event not found"}), 404


# Delete Event
@app.route("/events/<event_id>", methods=["DELETE"])
def delete_event(event_id):
    global events
    events = [e for e in events if e["id"] != event_id]
    save_events(events, DATA_FILE)
    return jsonify({"message": "Event deleted"})

import threading
import time
from datetime import timedelta

def check_reminders():
    reminded_ids = set() 

    while True:
        now = datetime.now()
        upcoming = [
            e for e in events
            if datetime.fromisoformat(e["start_time"]) <= now + timedelta(hours=1)
            and datetime.fromisoformat(e["start_time"]) > now
            and e["id"] not in reminded_ids  
        ]

        for e in upcoming:
            print(f"🔔 Reminder: '{e['title']}' starts at {e['start_time']}")
            send_email(
                subject="Event Reminder",
                message=f"Reminder: '{e['title']}' starts at {e['start_time']}",
                to_email="recipient@example.com"
            )
            reminded_ids.add(e["id"])  

        time.sleep(60)


reminder_thread = threading.Thread(target=check_reminders, daemon=True)
reminder_thread.start()



if __name__ == "__main__":
    app.run(debug=True)
