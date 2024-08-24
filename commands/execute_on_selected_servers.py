import asyncio
import paramiko
from telegram import Update
from telegram.ext import CallbackContext
from utils.db import Database
from utils.encryption import Encryption
from utils.logging import bot_logger

db = Database()
encryption = Encryption()

async def execute_on_selected_servers(update: Update, context: CallbackContext) -> None:
    selected_servers = context.user_data.get('selected_servers', [])
    if not selected_servers:
        await update.callback_query.message.reply_text("未选择任何服务器。")
        return

    message = await update.callback_query.message.reply_text("开始执行命令...")

    async def run_command_on_server(alias):
        server = db.get_server(update.effective_user.id, alias)
        if not server:
            return alias, None, "服务器未找到"

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if server[7]:  # 如果提供了密钥字符串
                key_data = encryption.decrypt(server[7])
                pkey = paramiko.RSAKey.from_private_key(key_data)
                ssh.connect(
                    hostname=server[3],
                    username=server[4],
                    port=server[6],
                    pkey=pkey
                )
            else:  # 使用密码连接
                ssh.connect(
                    hostname=server[3],
                    username=server[4],
                    password=encryption.decrypt(server[5]),
                    port=server[6]
                )

            stdin, stdout, stderr = ssh.exec_command(context.user_data.get('command'))
            output = stdout.read().decode() + stderr.read().decode()
            ssh.close()
            return alias, output, None
        except Exception as e:
            return alias, None, str(e)

    tasks = [run_command_on_server(alias) for alias in selected_servers]
    results = await asyncio.gather(*tasks)

    output_text = ""
    for alias, output, error in results:
        if error:
            output_text += f"服务器 {alias} 执行失败: {error}\n"
        else:
            output_text += f"服务器 {alias} 执行结果:\n{output}\n"

    await message.edit_text(output_text)
