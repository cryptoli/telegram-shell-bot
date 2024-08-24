from telegram import Update
from telegram.ext import CallbackContext
from utils.logging import bot_logger

async def exec_command(update: Update, context:
CallbackContext) -> None:
    command = update.message.text.strip()
    context.user_data['command'] = command

    selected_servers = context.user_data.get('selected_servers', [])
    if not selected_servers:
        await update.message.reply_text("请先选择一个或多个服务器，使用 /listservers 选择。")
        return

    await update.message.reply_text(f"已选择的服务器: {', '.join(selected_servers)}\n正在执行命令: {command}")
    bot_logger.info(f"用户 {update.effective_user.id} 在服务器 {', '.join(selected_servers)} 上执行命令: {command}")
