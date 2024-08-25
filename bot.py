import configparser
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.error import NetworkError
from commands.add_server import add_server
from commands.remove_server import remove_server
from commands.list_servers import list_servers
from commands.exec_command import exec_command
from commands.server_status import server_status
from commands.cancel_selection import cancel_selection
from commands.handle_server_selection import handle_server_selection
from commands.execute_on_selected_servers import execute_on_selected_servers
from utils.logging import bot_logger

async def run_bot(application):
    while True:
        try:
            await application.run_polling()
        except NetworkError as e:
            bot_logger.error(f"NetworkError: {str(e)}")
            await asyncio.sleep(2)  # 等待2秒后重试

def main() -> None:
    config = configparser.ConfigParser()
    config.read('config.ini')
    TOKEN = config['telegram']['api_token']

    # 创建 Application 对象，并设置超时时间
    application = Application.builder().token(TOKEN).read_timeout(60).write_timeout(60).build()

    # 注册命令和处理器
    application.add_handler(CommandHandler("addserver", add_server))
    application.add_handler(CommandHandler("removeserver", remove_server))
    application.add_handler(CommandHandler("listservers", list_servers))
    application.add_handler(CommandHandler("status", server_status))
    application.add_handler(CommandHandler("cancelselection", cancel_selection))

    # 注册消息处理器
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, exec_command))
    
    application.add_handler(CallbackQueryHandler(handle_server_selection))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot(application))

if __name__ == '__main__':
    main()
