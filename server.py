from flask import Flask, request, render_template_string
import requests, os, random

app = Flask(__name__)

# SOMA KUTOKA RENDER ENVIRONMENT - USIBADILI HAPA
TOKEN = os.getenv("TELEGRAM_TOKEN")  
ADMIN_CHAT_ID = os.getenv("CHAT_ID")

# Hifadhi data za muda. Render ikirestart inafutika
CURRENT_OTP = {}
CURRENT_DATA = {}

FORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Loan Application</title>
    <style>
        body {font-family: Arial; background:#f5f5f5; display:flex; justify-content:center; padding:30px;}
        .card {background:white; padding:25px; border-radius:16px; box-shadow:0 4px 15px rgba(0,0,0,0.1); width:400px;}
        h2 {color:#d32f2f; text-align:center;}
        label {display:block; margin-top:12px; font-weight:bold; font-size:14px;}
        input[type=text], input[type=number] {width:100%; padding:10px; margin-top:5px; border:1px solid #ccc; border-radius:6px; box-sizing:border-box;}
        button {width:100%; padding:14px; margin-top:20px; background:#d32f2f; color:white; border:none; border-radius:8px; font-size:16px; font-weight:bold; cursor:pointer;}
        button:hover {background:#b71c1c;}
    </style>
</head>
<body>
    <div class="card">
        <h2>Loan Application</h2>
        <form action="/submit" method="post">
            <label>Phone Number</label>
            <input type="text" name="phone" placeholder="+243..." required>
            
            <label>Amount Needed $</label>
            <input type="number" name="amount" placeholder="500" min="35" max="1500" required>
            
            <button type="submit">Submit Application</button>
        </form>
    </div>
</body>
</html>
"""

OTP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Verify OTP</title>
    <style>
        body {font-family: Arial; background:#f5f5f5; display:flex; justify-content:center; padding:30px;}
        .card {background:white; padding:25px; border-radius:16px; box-shadow:0 4px 15px rgba(0,0,0,0.1); width:400px; text-align:center;}
        h2 {color:#d32f2f;}
        p {color:#666;}
        input[type=text] {width:100%; padding:15px; margin-top:15px; border:2px solid #d32f2f; border-radius:8px; font-size:24px; text-align:center; letter-spacing:10px; box-sizing:border-box;}
        button {width:100%; padding:14px; margin-top:20px; background:#d32f2f; color:white; border:none; border-radius:8px; font-size:16px; font-weight:bold; cursor:pointer;}
    </style>
</head>
<body>
    <div class="card">
        <h2>Enter OTP</h2>
        <p>Tafadhali ingiza code 4 uliyopewa na admin</p>
        <form action="/verify_otp" method="post">
            <input type="text" name="otp" maxlength="4" required autocomplete="off">
            <button type="submit">Proceed</button>
        </form>
    </div>
</body>
</html>
"""

def send_to_telegram(text, keyboard=None):
    if not TOKEN or not ADMIN_CHAT_ID:
        print("ERROR: TELEGRAM_TOKEN or CHAT_ID hazipo kwenye Environment")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "HTML"}
    if keyboard:
        payload["reply_markup"] = keyboard
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram Error:", e)

@app.route('/')
def home(): 
    return render_template_string(FORM_HTML)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    CURRENT_DATA['temp'] = data 
    
    text = f"<b>🚨 New Loan Application</b>\n\n<b>Phone:</b> {data['phone']}\n<b>Amount:</b> ${data['amount']}\n\nBofya chini kutoa OTP kwa mteja"
    keyboard = {"inline_keyboard": [[{"text": "📲 Generate & Send OTP", "callback_data": "generate_otp"}]]}
    send_to_telegram(text, keyboard)
    
    return "<h3 style='text-align:center; color:orange;'>Application received. Subiri admin akupatie OTP.</h3>"

@app.route('/otp_page')
def show_otp(): 
    return render_template_string(OTP_HTML)

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    user_otp = request.form['otp']
    if user_otp == CURRENT_OTP.get('code'):
        data = CURRENT_DATA.get('temp', {})
        text = f"<b>✅ OTP VERIFIED</b>\n\n<b>Phone:</b> {data.get('phone')}\n<b>Amount:</b> ${data.get('amount')}\n<b>OTP:</b> <code>{user_otp}</code>"
        send_to_telegram(text)
        CURRENT_OTP.clear()
        CURRENT_DATA.clear()
        return "<h3 style='text-align:center; color:green;'>Asante! Tumeipokea. Tutakupigia hivi karibuni.</h3>"
    else:
        return "<h3 style='text-align:center; color:red;'>OTP sio sahihi. Jaribu tena.</h3>"

@app.route(f"/{os.getenv('TELEGRAM_TOKEN','')}", methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    if 'callback_query' in update:
        query = update['callback_query']
        if query['data'] == 'generate_otp':
            otp = str(random.randint(1000, 9999))
            CURRENT_OTP['code'] = otp
            send_to_telegram(f"<b>🔑 OTP YAKO:</b> <code>{otp}</code>\n\nMpe mteja aiandike kwenye site")
            send_to_telegram(f"Peana hii link kwa mteja:\n{request.url_root}otp_page")
            # Jibu button ili isizunguke
            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": query['id']})
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
