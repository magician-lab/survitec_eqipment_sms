from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from services.taifa import send_sms

load_dotenv()

app = Flask(__name__)


# =========================
# UI PAGE
# =========================
@app.route("/sms", methods=["GET"])
def sms_page():
    return render_template("sms.html")


# =========================
# HEALTH CHECK (IMPORTANT DEBUG TOOL)
# =========================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"})


# =========================
# SMS API (STRICT JSON ONLY)
# =========================
@app.route("/send_sms", methods=["GET", "POST"])
def send_sms_route():

    print("\n🔥 ROUTE HIT: /send_sms")

    # Check headers
    content_type = request.headers.get("Content-Type")
    print("CONTENT-TYPE:", content_type)

    # Read raw body
    raw_body = request.data
    print("RAW BODY:", raw_body)

    # Parse JSON safely
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Invalid or missing JSON",
            "hint": "Frontend must send application/json",
            "received_content_type": content_type,
            "raw_body": raw_body.decode("utf-8", errors="ignore")
        }), 400

    print("JSON RECEIVED:", data)

    # Validate fields
    numbers = data.get("numbers")
    message = data.get("message")

    if not numbers:
        return jsonify({"error": "Missing numbers"}), 400

    if not message:
        return jsonify({"error": "Missing message"}), 400

    # Send SMS
    results = []

    for num in numbers:
        try:
            response = send_sms(num, message)

            results.append({
                "number": num,
                "status": "sent",
                "response": response
            })

        except Exception as e:
            results.append({
                "number": num,
                "status": "failed",
                "error": str(e)
            })

    return jsonify({
        "status": "success",
        "count": len(numbers),
        "results": results
    })


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    print("🔥 Starting Flask on http://127.0.0.1:5050")
    app.run(
        host="0.0.0.0",
        port=5050,
        debug=True
    )