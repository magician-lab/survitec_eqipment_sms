from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from services.taifa import send_sms
import os
import logging

# =========================
# CONFIG
# =========================
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("SMS_API_KEY")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================
# UI PAGE (FOR TESTING)
# =========================
@app.route("/sms", methods=["GET"])
def sms_page():
    return render_template("sms.html")


# =========================
# HEALTH CHECK
# =========================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "running"
    })


# =========================
# ODOO / API ENDPOINT
# =========================
@app.route("/api/send_sms", methods=["POST"])
def send_sms_route():

    logging.info("SMS request received")

    # -------------------------
    # API KEY VALIDATION
    # -------------------------
    supplied_key = request.headers.get("X-API-KEY")

    if API_KEY:
        if supplied_key != API_KEY:
            logging.warning("Unauthorized request")

            return jsonify({
                "success": False,
                "error": "Unauthorized"
            }), 401

    # -------------------------
    # JSON VALIDATION
    # -------------------------
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid or missing JSON"
        }), 400

    numbers = data.get("numbers", [])
    message = data.get("message", "")

    if not numbers:
        return jsonify({
            "success": False,
            "error": "Missing numbers"
        }), 400

    if not message:
        return jsonify({
            "success": False,
            "error": "Missing message"
        }), 400

    logging.info(
        f"Sending SMS to {len(numbers)} recipient(s)"
    )

    # -------------------------
    # SEND SMS
    # -------------------------
    results = []
    success_count = 0
    failed_count = 0

    for num in numbers:

        try:
            response = send_sms(num, message)

            results.append({
                "number": num,
                "status": "sent",
                "response": response
            })

            success_count += 1

        except Exception as e:

            logging.exception(
                f"Failed sending SMS to {num}"
            )

            results.append({
                "number": num,
                "status": "failed",
                "error": str(e)
            })

            failed_count += 1

    return jsonify({
        "success": True,
        "total_numbers": len(numbers),
        "sent_count": success_count,
        "failed_count": failed_count,
        "results": results
    })


# =========================
# LOCAL DEVELOPMENT ONLY
# =========================
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5050)),
        debug=True
    )
