import logging
import re
from time import sleep
from typing import Dict
from flask import Flask, request, jsonify
from collections import deque
from datetime import datetime, timedelta

app = Flask(__name__)

webhook_data = deque(maxlen=10)

def generate_response(status, data):
    return jsonify({
        "status": status,
        "data": data,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def get_latest_data(maxage=None):
    if webhook_data:
        latest_entry = webhook_data[-1]
        latest_timestamp = datetime.strptime(latest_entry['timestamp'], "%Y-%m-%d %H:%M:%S")
        
        if maxage is not None:
            age_limit = datetime.now() - timedelta(seconds=maxage)
            if latest_timestamp >= age_limit:
                return True, latest_entry
            else:
                return False, "Latest entry is older than the specified maxage"
        else:
            return True, latest_entry
    else:
        return False, "No data available"

def getOTP():
    OTP_REGEX = r"\b\d{6}\b"
    max_attempts = 12
    attempt = 0
    while attempt < max_attempts:
        sleep(5)
        attempt+=1
        logging.info(f"Attemptng to get OTP:{attempt}")
        status, data = get_latest_data(60)
        if(status):
            logging.log(logging.INFO, "OTP received")
            otp = re.findall(OTP_REGEX, data["data"]["text"])
            return otp[0] if otp else None
        else :
            logging.log(logging.INFO, "No OTP received")
    return None

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.is_json:
        data = request.json
        timestamped_data = {
            "data": data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        webhook_data.append(timestamped_data)
        print(f"Received and stored webhook data: {timestamped_data}")
        return generate_response(True, "Webhook data received successfully")
    else:
        return generate_response(False, "Invalid or missing JSON data"), 400

@app.route('/latest', methods=['GET'])
def latest_data():
    maxage = request.args.get('maxage', type=int)
    status, data = get_latest_data(maxage)
    return generate_response(status, data)

@app.route('/trigger', methods=['GET'])
def trigger():
    getOTP()
    return generate_response(True, "OTP triggered")

@app.route('/all', methods=['GET'])
def view_data():
    return generate_response(True, list(webhook_data))

if __name__ == '__main__':
    app.run(port=5000, debug=True)

