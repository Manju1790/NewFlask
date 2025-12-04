from flask import Flask, render_template, request, redirect
import requests
import uuid

app = Flask(__name__)

# ------------------ CONFIG ---------------------
FIREBASE_BASE_URL = "https://workshop-ec1b0-default-rtdb.firebaseio.com/"
REGISTRATIONS_URL = f"{FIREBASE_BASE_URL}/registrations"
# -----------------------------------------------

# Static events for simplicity (you can also put these in Firebase if you want)
EVENTS = [
    {"id": "hackathon", "title": "Hackathon 2025", "date": "2025-03-10", "venue": "Auditorium"},
    {"id": "tech_talk_ai", "title": "Tech Talk: AI & ML", "date": "2025-03-15", "venue": "Seminar Hall"},
    {"id": "cultural_fest", "title": "Cultural Fest", "date": "2025-03-25", "venue": "Open Stage"},
]


def get_event_by_id(event_id):
    for e in EVENTS:
        if e["id"] == event_id:
            return e
    return None


@app.route("/")
def home():
    return render_template("home.html", events=EVENTS)


@app.route("/register/<event_id>", methods=["GET", "POST"])
def register(event_id):
    event = get_event_by_id(event_id)
    if not event:
        return "Event not found", 404

    if request.method == "POST":
        data = {
            "event_id": event_id,
            "name": request.form["name"],
            "department": request.form["department"],
            "email": request.form["email"],
            "phone": request.form["phone"]
        }
        # unique id for this registration
        reg_id = uuid.uuid4().hex
        # PUT to /registrations/<reg_id>.json
        requests.put(f"{REGISTRATIONS_URL}/{reg_id}.json", json=data)
        return redirect("/success")

    return render_template("register.html", event=event)


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/participants/<event_id>")
def participants(event_id):
    event = get_event_by_id(event_id)
    if not event:
        return "Event not found", 404

    # GET all registrations
    res = requests.get(f"{REGISTRATIONS_URL}.json")
    data = res.json() or {}

    # filter for this event
    regs = []
    for reg_id, reg in data.items():
        if reg.get("event_id") == event_id:
            regs.append({"id": reg_id, **reg})

    return render_template("participants.html", event=event, regs=regs)


@app.route("/delete/<reg_id>/<event_id>")
def delete_registration(reg_id, event_id):
    # DELETE /registrations/<reg_id>.json
    requests.delete(f"{REGISTRATIONS_URL}/{reg_id}.json")
    return redirect(f"/participants/{event_id}")


if __name__ == "__main__":
    app.run(debug=True)
