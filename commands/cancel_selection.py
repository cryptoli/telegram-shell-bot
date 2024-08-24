from telegram import Update
from telegram.ext import CallbackContext
from utils.logging import bot_logger

async def cancel_selection(update: Update, context: CallbackContext) -> None:
    try:
        context.user_data.pop('selected_server', None)
        await update.message.reply_text("服务器选择已取消。")
        bot_logger.info(f"用户 {update.effective_user.id} 取消了服务器选择。")
    except Exception as e:
        bot_logger.error(f"取消选择服务器出错: {str(e)}")
        await update.message.reply_text(f"取消选择服务器失败: {str(e)}")
