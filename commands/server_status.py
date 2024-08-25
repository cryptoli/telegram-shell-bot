import asyncio
import paramiko
from telegram import Update
from telegram.ext import CallbackContext
from utils.encryption import Encryption
from utils.db import Database
from utils.logging import bot_logger

db = Database()
encryption = Encryption()

async def server_status(update: Update, context: CallbackContext) -> None:
    selected_servers = context.user_data.get('selected_servers', [])
    if not selected_servers:
        await update.message.reply_text("请先选择一个或多个服务器。使用 /listservers 选择服务器。")
        return

    message = await update.message.reply_text("开始获取服务器状态...")

    async def get_status(alias):
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
                    hostname=server[2],
                    username=server[3],
                    port=server[5],
                    pkey=pkey
                )
            else:  # 使用密码连接
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

            # 获取网络流量使用情况
            stdin, stdout, stderr = ssh.exec_command("ifstat -i eth0 1 1 | awk 'NR==3 {print $1\"KB/s RX, \"$2\"KB/s TX\"}'")
            network_info = stdout.read().decode().strip()

            status_info = (
                f"Server:{alias} "
                f"CPU:{cpu_cores} {cpu_usage}% "
                f"Memory:{memory_info} "
                f"Disk:{disk_info} "
                f"LoadInfo:{load_info} "
                f"Network:{network_info}\n"
            )

            ssh.close()
            return alias, status_info, None
        except Exception as e:
            return alias, None, str(e)

    # 异步获取状态
    tasks = [get_status(alias) for alias in selected_servers]
    results = await asyncio.gather(*tasks)

    # 处理获取的状态并分块发送消息
    output_text = ""
    for alias, status_info, error in results:
        if error:
            output_text += f"服务器 {alias} 获取状态失败: {error}\n"
        else:
            output_text += f"服务器 {alias} 状态:\n{status_info}\n"

    # 分块发送消息，避免 Message_too_long 错误
    chunk_size = 4000  # 保留些许余量，避免刚好超过限制
    for i in range(0, len(output_text), chunk_size):
        await message.edit_text(output_text[i:i+chunk_size])
        if i + chunk_size < len(output_text):
            # 如果还有剩余内容，发送一条新消息，并更新 message 对象以继续编辑后续内容
            message = await update.message.reply_text(output_text[i+chunk_size:i+2*chunk_size])

    bot_logger.info(f"用户 {update.effective_user.id} 查看了服务器 {', '.join(selected_servers)} 的状态。")
