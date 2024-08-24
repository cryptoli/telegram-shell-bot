from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.db import Database
from utils.logging import bot_logger

db = Database()

async def list_servers(update: Update, context: CallbackContext) -> None:
    try:
        servers = db.get_servers(update.effective_user.id)
        
        if not servers:
            await update.message.reply_text("没有已添加的服务器。")
            return
        
        keyboard = [
            [InlineKeyboardButton(s[2], callback_data=s[2])]
            for s in servers
        ]
        keyboard.append([InlineKeyboardButton("取消选择", callback_data="cancel_selection")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("请选择一个服务器:", reply_markup=reply_markup)
        bot_logger.info(f"用户 {update.effective_user.id} 列出了服务器。")
    except Exception as e:
        bot_logger.error(f"列出服务器出错: {str(e)}")
        await update.message.reply_text(f"列出服务器失败: {str(e)}")
