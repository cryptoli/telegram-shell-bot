import paramiko
from telegram import Update
from telegram.ext import CallbackContext
from utils.encryption import Encryption
from utils.db import Database
from utils.logging import bot_logger

db = Database()
encryption = Encryption()

async def exec_command(update: Update, context: CallbackContext) -> None:
    try:
        command = update.message.text.strip()
        host = context.user_data.get('selected_server')

        if not host:
            await update.message.reply_text("请先选择一个服务器。使用 /listservers 选择一个服务器。")
            return

        server = db.get_server(update.effective_user.id, host)
        if not server:
            await update.message.reply_text("所选服务器未找到。")
            return

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if server[6]:  # 如果提供了密钥字符串
            key_data = encryption.decrypt(server[6])
            pkey = paramiko.RSAKey.from_private_key(key_data)
            ssh.connect(
                hostname=server[2],
                username=server[3],
                port=server[5],
                pkey=pkey
            )
        else:  # 如果没有提供密钥字符串，使用密码连接
            ssh.connect(
                hostname=server[2],
                username=server[3],
                password=encryption.decrypt(server[4]),
                port=server[5]
            )

        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode() + stderr.read().decode()
        
        if not output.strip():
            output = "执行成功。"

        await update.message.reply_text(f"输出:\n{output}")
        bot_logger.info(f"用户 {update.effective_user.id} 在服务器 {host} 上执行了命令: {command}")
        ssh.close()
    except Exception as e:
        bot_logger.error(f"执行命令出错: {str(e)}")
        await update.message.reply_text(f"执行命令失败: {str(e)}")
