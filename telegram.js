const TelegramBot = require('node-telegram-bot-api');
const BOT_TOKEN = process.env.BOT_TOKEN;

const bot = new TelegramBot(BOT_TOKEN, {polling: true});

bot.on('callback_query', async (query) => {
  const [action, loanId] = query.data.split('_');
  const chatId = query.message.chat.id;
  
  if(action === 'approve'){
    bot.sendMessage(chatId, `Loan ${loanId} Approved ✅. User atapata SMS`);
    // Hapa unaeza update DB: status = approved
  } 
  if(action === 'reject'){
    bot.sendMessage(chatId, `Loan ${loanId} Rejected ❌`);
  }
  
  bot.answerCallbackQuery(query.id);
});
