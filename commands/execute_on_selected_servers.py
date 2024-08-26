import asyncio
import paramiko
from telegram import Update
from telegram.ext import CallbackContext
from utils.db import Database
from utils.encryption import Encryption
from utils.logging import bot_logger
from .executor_pool import submit_task  # 导入线程池提交函数

db = Database()
encryption = Encryption()

async def execute_on_selected_servers(update: Update, context: CallbackContext) -> None:
    selected_servers = context.user_data.get('selected_servers', [])
    if not selected_servers:
        await update.message.reply_text("未选择任何服务器。")
        return

    # 初始化一个初始消息
    message = await update.message.reply_text("开始执行命令...\n")

    def run_command_on_server(alias):
        server = db.get_server(update.effective_user.id, alias)
        if not server:
            return alias, None, "服务器未找到"

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if server[7]:  # 如果提供了密钥字符串
                key_data = encryption.decrypt(server[7])
                pkey = paramiko.RSAKey.from_private_key_string(key_data)
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

    # 使用线程池并发执行命令
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(None, submit_task, run_command_on_server, alias) for alias in selected_servers]
    results = await asyncio.gather(*tasks)

    # 实时更新消息内容
    combined_output = "开始执行命令...\n"
    for future in results:
        alias, output, error = future.result()  # 调用 result() 方法获取结果
        if error:
            combined_output += f"服务器 {alias} 执行失败: {error}\n\n"
        else:
            combined_output += (
                f"服务器 {alias} 执行结果:\n"
                f"```\n"
                f"{output}\n"
                f"```\n"
                f"{'-'*40}\n\n"  # 分隔符
            )
        # 更新消息内容
        await message.edit_text(combined_output, parse_mode='Markdown')
        bot_logger.info(f"用户 {update.effective_user.id} 在服务器 {alias} 上执行命令: {context.user_data.get('command')}")

    # 最终更新消息，标记所有命令执行完毕
    combined_output += "所有命令执行完毕。\n"
    await message.edit_text(combined_output, parse_mode='Markdown')

