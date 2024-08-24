from telegram import Update
from telegram.ext import CallbackContext
from utils.encryption import Encryption
from utils.db import Database
from utils.logging import bot_logger

db = Database()
encryption = Encryption()

async def add_server(update: Update, context: CallbackContext) -> None:
    try:
        if len(context.args) < 4:
            await update.message.reply_text("用法: /addserver <别名> <用户名> <主机> <密码或密钥> [<端口>] [<是否使用密钥>]")
            return
        
        alias = context.args[0]
        username = context.args[1]
        host = context.args[2]
        credential = context.args[3]
        port = int(context.args[4]) if len(context.args) > 4 else 22
        use_key = context.args[5].lower() == 'true' if len(context.args) > 5 else False

        if use_key:
            key_data = encryption.encrypt(credential)
            password = None
        else:
            password = encryption.encrypt(credential)
            key_data = None
        
        db.add_server(update.effective_user.id, alias, host, username, password, port, key_data)
        await update.message.reply_text(f"服务器 {alias} 添加成功。")
        bot_logger.info(f"用户 {update.effective_user.id} 添加了服务器 {alias} ({host})。")
    except Exception as e:
        bot_logger.error(f"添加服务器出错: {str(e)}")
        await update.message.reply_text(f"添加服务器失败: {str(e)}")
