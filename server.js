const express = require('express');
const TelegramBot = require('node-telegram-bot-api');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

const bot = new TelegramBot(process.env.BOT_TOKEN);
const CHAT_ID = process.env.CHAT_ID;

app.use(cors());
app.use(express.json());

app.post('/submit', async (req, res) => {
    try {
        const { name, phone, amount, message } = req.body;
        const text = `🚨 LOAN APPLICATION MPYA 🚨\n\nJina: ${name}\nSimu: ${phone}\nKiasi: ${amount}\nUjumbe: ${message}`;
        await bot.sendMessage(CHAT_ID, text);
        res.json({ success: true });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

app.get('/', (req, res) => {
    res.send('Loan Backend is Running ✅');
});

app.listen(PORT, () => console.log('Running on ' + PORT));
