from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Loan API is running!"})

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
