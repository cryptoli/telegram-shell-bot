import asyncio
import paramiko
import traceback
from telegram import Update
from telegram.ext import CallbackContext
from cryptography.fernet import InvalidToken
from utils.encryption import Encryption
from utils.db import Database
from utils.logging import bot_logger
from datetime import datetime
from telegram.error import BadRequest
from .executor_pool import submit_task  # 导入线程池提交函数

db = Database()
encryption = Encryption()

async def server_status(update: Update, context: CallbackContext) -> None:
    selected_servers = context.user_data.get('selected_servers', [])
    if not selected_servers:
        await update.message.reply_text("请先选择一个或多个服务器。使用 /listservers 选择服务器。")
        return

    message = await update.message.reply_text("开始获取服务器状态...")
    last_message_text = message.text  # 记录上一次发送的消息内容

    async def run_command(ssh, command, alias, desc):
        try:
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode().strip()
            error_output = stderr.read().decode().strip()
            if error_output:
                bot_logger.error(f"服务器 {alias} 执行 {desc} 命令时出错：{error_output}")
                return None, f"Error - {error_output}"
            return output, None
        except Exception as e:
            bot_logger.error(f"服务器 {alias} 执行 {desc} 命令时异常：{str(e)}")
            return None, str(e)

    async def get_os_type(ssh, alias):
        output, _ = await run_command(ssh, "cat /etc/os-release", alias, "获取操作系统类型")
        if "Ubuntu" in output or "Debian" in output:
            return "debian"
        elif "CentOS" in output or "Red Hat" in output:
            return "rhel"
        else:
            return "unknown"

    async def check_and_install(ssh, tool_name, package_name, os_type, alias):
        check_command = f"command -v {tool_name} >/dev/null 2>&1 && echo 'installed' || echo 'not installed'"
        output, _ = await run_command(ssh, check_command, alias, f"检查 {tool_name} 是否安装")

        if 'not installed' in output:
            bot_logger.info(f"服务器 {alias} 未检测到 {tool_name}，正在安装...")
            
            if os_type == "debian":
                update_command = "sudo apt-get update"
                install_command = f"sudo DEBIAN_FRONTEND=noninteractive apt-get install -y {package_name}"
            elif os_type == "rhel":
                install_command = f"sudo yum install -y {package_name}"
            else:
                return False, f"无法自动安装 {tool_name}：不支持的操作系统类型。"

            await run_command(ssh, update_command, alias, "更新包管理器缓存")
            _, error_output = await run_command(ssh, install_command, alias, f"安装 {tool_name}")

            if error_output:
                return False, f"安装 {tool_name} 时出错：{error_output}"
            else:
                return True, f"{tool_name} 安装成功。"
        else:
            return True, None  # 如果已安装，返回None，不输出信息

    async def get_active_interface(ssh, alias):
        command = "ip route | grep default | awk '{print $5}'"
        output, _ = await run_command(ssh, command, alias, "检测最活跃的网络接口")
        return output if output else "eth0"

    def get_status(alias):
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
                try:
                    password = encryption.decrypt(server[5])
                except InvalidToken:
                    bot_logger.error(f"解密服务器 {alias} 的密码时发生错误：无效的加密数据。")
                    return alias, None, "解密密码时出错：无效的加密数据。"

                ssh.connect(
                    hostname=server[3],
                    username=server[4],
                    password=password,
                    port=server[6]
                )

            os_type = asyncio.run(get_os_type(ssh, alias))
            
            tools = {'mpstat': 'sysstat', 'ifstat': 'ifstat'}
            for tool, package in tools.items():
                success, install_msg = asyncio.run(check_and_install(ssh, tool, package, os_type, alias))
                if not success:
                    ssh.close()
                    return alias, None, install_msg

            active_interface = asyncio.run(get_active_interface(ssh, alias))

            commands = {
                "CPU 核数": "grep -c ^processor /proc/cpuinfo",
                "CPU 占用率": "mpstat | awk '$3 ~ /all/ {print 100 - $13}'",
                "内存使用": "free -m | awk 'NR==2{printf \"%sMB/%sMB (%.2f%%)\", $3,$2,$3*100/$2 }'",
                "磁盘使用": "df -h --total | grep 'total' | awk '{print $3 \"/\" $2 \" (\" $5 \")\"}'",
                "系统负载": "uptime | awk -F'[a-z]:' '{ print $2 }'",
                "网络流量": f"ifstat -i {active_interface} 1 1 | awk 'NR==3 {{print $1\"KB/s RX, \"$2\"KB/s TX\"}}'",
                "流量使用量(G)": f"ifstat -i {active_interface} -b -q 1 1 | awk 'NR==3 {{printf \"%.2f GB RX, %.2f GB TX\", $1/1024/1024, $2/1024/1024}}'"
            }

            status_info = f"服务器 {alias} 状态:\n"

            for desc, cmd in commands.items():
                output, error_output = asyncio.run(run_command(ssh, cmd, alias, desc))

                if output:
                    if desc == "CPU 占用率":
                        status_info += f"{desc}: {output}%\n"
                    else:
                        status_info += f"{desc}: {output}\n"
                elif error_output:
                    status_info += f"{desc}: {error_output}\n"
                else:
                    status_info += f"{desc}: 无法获取到数据\n"
                    bot_logger.debug(f"服务器 {alias} 执行 {desc} 命令时未返回任何输出。")

            ssh.close()

            status_info = (
                f"**服务器 {alias} 状态:**\n"
                f"```\n"
                f"{status_info}\n"
                f"```\n"
                f"*更新于: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            )

            return alias, status_info, None
        except Exception as e:
            error_message = traceback.format_exc()
            bot_logger.error(f"获取服务器 {alias} 状态时出错: {error_message}")
            return alias, None, str(e)

    combined_output = "开始获取服务器状态...\n"
    try:
        await message.edit_text(combined_output)
    except BadRequest:
        pass  # 捕获 BadRequest 错误，如果内容没有变化则跳过
    last_message_text = combined_output  # 初始化上一次消息内容

    loop = asyncio.get_event_loop()

    # 使用线程池并发执行任务
    tasks = [loop.run_in_executor(None, submit_task, get_status, alias) for alias in selected_servers]
    results = await asyncio.gather(*tasks)

    for future in results:
        alias, status_info, error = future.result()  # 调用 result() 方法获取结果
        if error:
            combined_output += f"服务器 {alias} 获取状态失败: {error}\n\n"
        else:
            combined_output += f"{status_info}\n"

        new_text = f"{combined_output}\n更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if new_text != last_message_text:
            try:
                await message.edit_text(new_text, parse_mode='Markdown')
                last_message_text = new_text  # 更新上一次消息内容
            except BadRequest:
                pass  # 捕获 BadRequest 错误，如果内容没有变化则跳过

    combined_output += "所有服务器状态获取完毕。\n"
    final_text = f"{combined_output}\n更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if final_text != last_message_text:
        try:
            await message.edit_text(final_text, parse_mode='Markdown')
        except BadRequest:
            pass  # 捕获 BadRequest 错误，如果内容没有变化则跳过

    bot_logger.info(f"用户 {update.effective_user.id} 查看了服务器 {', '.join(selected_servers)} 的状态。")

