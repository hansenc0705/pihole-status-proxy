import os
import requests
import urllib3
from flask import Flask, jsonify

# Suppress HTTPS warnings (for self-signed certs)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

PIHOLE_URL = os.environ.get("PIHOLE_URL")
PIHOLE_PASSWORD = os.environ.get("PIHOLE_PASSWORD")

@app.route("/")
def check_blocking():
    if not PIHOLE_URL or not PIHOLE_PASSWORD:
        print("Missing PIHOLE_URL or PIHOLE_PASSWORD", flush=True)
        return jsonify({"error": "PIHOLE_URL or PIHOLE_PASSWORD not set"}), 500

    auth_url = f"{PIHOLE_URL}/api/auth"
    status_url = f"{PIHOLE_URL}/api/dns/blocking"

    session = requests.Session()

    try:
        # Step 1: Authenticate
        auth_response = session.post(auth_url, json={"password": PIHOLE_PASSWORD}, verify=False)
        print("Auth response status:", auth_response.status_code, flush=True)
        print("Auth response body:", auth_response.text, flush=True)

        auth_response.raise_for_status()
        json_data = auth_response.json()
        sid = json_data.get("session", {}).get("sid")
        csrf = json_data.get("session", {}).get("csrf")

        if not sid or not csrf:
            print("SID or CSRF token missing", flush=True)
            return jsonify({"error": "Missing SID or CSRF token"}), 500

        # Step 2: Check blocking status (with CSRF token header)
        headers = {
            "X-CSRF-Token": csrf
        }
        status_response = session.get(status_url, headers=headers, verify=False)
        status_response.raise_for_status()
        data = status_response.json()
        print("Blocking status data:", data, flush=True)

        return data

    except Exception as e:
        print("Exception occurred:", str(e), flush=True)
        return jsonify({"error": str(e)}), 500

    finally:
        # Step 3: Logout using the SID
        if 'sid' in locals() and sid:
            logout_url = f"{PIHOLE_URL}/api/auth?sid={sid}"
            try:
                logout_response = session.delete(logout_url, verify=False)
                print("Logged out:", logout_response.status_code, flush=True)
            except Exception as logout_err:
                print("Logout error:", str(logout_err), flush=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)