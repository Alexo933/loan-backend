const express = require('express');
const axios = require('axios'); // 1. add hii
const app = express();
app.use(express.json());

// 2. Weka hizi kwa .env kwa Render
const BOT_TOKEN = process.env.BOT_TOKEN;
const ADMIN_CHAT_ID = process.env.ADMIN_CHAT_ID;

app.post('/api/loan/submit', async (req, res) => {
  const { name, amount, docs, otp } = req.body;
  
  try {
    // 1. Verify OTP hapa
    // if(!verifyOTP(otp)) return res.status(400).json({error: "Invalid OTP"})
    
    // 2. Save to DB with status: pending_approval
    // const loanId = await saveToDB({name, amount, docs, status: "pending_approval"})
    const loanId = Date.now(); // temporary ID kama huna DB bado

    // 3. Tuma Telegram
    await axios.post(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      chat_id: ADMIN_CHAT_ID,
      text: `New Loan Request\n\nName: ${name}\nAmount: ${amount}\nID: ${loanId}`,
      reply_markup: {
        inline_keyboard: [
          [{text: "✅ Approve", callback_data: `approve_${loanId}`}],
          [{text: "❌ Reject", callback_data: `reject_${loanId}`}]
        ]
      }
    })

    res.json({success: true, message: "Submitted for approval", loanId})
  } catch (err) {
    res.status(500).json({error: err.message})
  }
});

app.listen(3000, () => console.log("Server running on 3000"));
