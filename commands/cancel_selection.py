from telegram import Update
from telegram.ext import CallbackContext
from utils.logging import bot_logger

async def cancel_selection(update: Update, context: CallbackContext) -> None:
    try:
        # 使用 update.callback_query.message 来获取消息对象
        query = update.callback_query
        await query.message.reply_text("服务器选择已取消。")
        
        # 清除已选服务器
        context.user_data.pop('selected_server', None)
        bot_logger.info(f"用户 {update.effective_user.id} 取消了服务器选择。")
    except Exception as e:
        await query.message.reply_text(f"取消选择服务器失败: {str(e)}")
        bot_logger.error(f"取消选择服务器出错: {str(e)}")
