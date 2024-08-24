import paramiko
from telegram import Update
from telegram.ext import CallbackContext
from utils.encryption import Encryption
from utils.db import Database
from utils.logging import bot_logger

db = Database()
encryption = Encryption()

async def server_status(update: Update, context: CallbackContext) -> None:
    try:
        selected_servers = context.user_data.get('selected_servers', [])
        
        if not selected_servers:
            await update.message.reply_text("请先选择一个或多个服务器。使用 /listservers 选择服务器。")
            return
        
        # 遍历选择的服务器，并获取每个服务器的状态
        for alias in selected_servers:
            server = db.get_server(update.effective_user.id, alias)
            if not server:
                await update.message.reply_text(f"所选服务器 '{alias}' 未找到。")
                continue

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if server[7]:  # 如果提供了密钥字符串
                key_data = encryption.decrypt(server[7])
                pkey = paramiko.RSAKey.from_private_key_string(key_data)
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

            # 获取 CPU 核数和占用百分比
            stdin, stdout, stderr = ssh.exec_command("grep -c ^processor /proc/cpuinfo")
            cpu_cores = stdout.read().decode().strip()
            stdin, stdout, stderr = ssh.exec_command("mpstat | awk '$3 ~ /all/ {print 100 - $13}'")
            cpu_usage = stdout.read().decode().strip()

            # 获取内存已使用量和总量
            stdin, stdout, stderr = ssh.exec_command("free -m | awk 'NR==2{printf \"%s/%sMB (%.2f%%)\", $3,$2,$3*100/$2 }'")
            memory_info = stdout.read().decode().strip()

            # 获取磁盘已使用量和总量
            stdin, stdout, stderr = ssh.exec_command("df -h --total | grep 'total' | awk '{print $3 \"/\" $2 \" (\" $5 \")\"}'")
            disk_info = stdout.read().decode().strip()

            # 获取系统负载
            stdin, stdout, stderr = ssh.exec_command("uptime | awk -F'[a-z]:' '{ print $2 }'")
            load_info = stdout.read().decode().strip()

            status_info = (
                f"服务器: {alias}\n"
                f"CPU 总核数: {cpu_cores}, 占用率: {cpu_usage}%\n"
                f"内存: {memory_info}\n"
                f"磁盘: {disk_info}\n"
                f"系统负载: {load_info}\n"
            )

            await update.message.reply_text(f"服务器状态:\n{status_info}")
            bot_logger.info(f"用户 {update.effective_user.id} 查看了服务器 {alias} 的状态。")
            ssh.close()
    except Exception as e:
        bot_logger.error(f"获取服务器状态出错: {str(e)}")
        await update.message.reply_text(f"获取服务器状态失败: {str(e)}")
