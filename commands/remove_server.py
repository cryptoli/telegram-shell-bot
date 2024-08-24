from telegram import Update
from telegram.ext import CallbackContext
from utils.db import Database
from utils.logging import bot_logger

db = Database()

async def remove_server(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) < 1:
            await update.message.reply_text("用法: /removeserver <主机>")
            return
        
        host = context.args[0]
        db.remove_server(update.effective_user.id, host)
        await update.message.reply_text(f"服务器 {host} 删除成功。")
        bot_logger.info(f"用户 {update.effective_user.id} 删除了服务器 {host}。")
    except Exception as e:
        bot_logger.error(f"删除服务器出错: {str(e)}")
        await update.message.reply_text(f"删除服务器失败: {str(e)}")
