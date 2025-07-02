import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

PIHOLE_URL = os.environ.get("PIHOLE_URL")
PIHOLE_PASSWORD = os.environ.get("PIHOLE_PASSWORD")

@app.route("/")
def check_blocking():
    if not PIHOLE_URL or not PIHOLE_PASSWORD:
        return jsonify({"error": "PIHOLE_URL or PIHOLE_PASSWORD not set"}), 500

    auth_url = f"{PIHOLE_URL}/api/auth"
    status_url = f"{PIHOLE_URL}/api/dns/blocking"

    session = requests.Session()

    try:
        # Step 1: Authenticate and get SID
        auth_response = session.post(auth_url, json={"password": PIHOLE_PASSWORD}, verify=False)
        auth_response.raise_for_status()
        sid = auth_response.json().get("sid")

        if not sid:
            return jsonify({"error": "No SID returned from Pi-hole"}), 500

        # Step 2: Use the session to check blocking status
        status_response = session.get(status_url, verify=False)
        status_response.raise_for_status()
        data = status_response.json()

        return data

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Step 3: Log out with DELETE request
        if 'sid' in locals() and sid:
            logout_url = f"{PIHOLE_URL}/api/auth?sid={sid}"
            try:
                session.delete(logout_url, verify=False)
            except:
                pass  # Swallow logout errors silently
