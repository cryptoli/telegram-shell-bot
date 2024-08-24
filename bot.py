import configparser
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from commands.add_server import add_server
from commands.remove_server import remove_server
from commands.list_servers import list_servers
from commands.exec_command import exec_command
from commands.server_status import server_status
from commands.cancel_selection import cancel_selection
from commands.handle_server_selection import handle_server_selection
from commands.execute_on_selected_servers import execute_on_selected_servers

def main() -> None:
    config = configparser.ConfigParser()
    config.read('config.ini')
    TOKEN = config['telegram']['api_token']
    
    application = Application.builder().token(TOKEN).build()

    # 注册命令和处理器
    application.add_handler(CommandHandler("addserver", add_server))
    application.add_handler(CommandHandler("removeserver", remove_server))
    application.add_handler(CommandHandler("listservers", list_servers))
    application.add_handler(CommandHandler("status", server_status))
    application.add_handler(CommandHandler("cancelselection", cancel_selection))

    # 注册消息处理器
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, exec_command))
    
    # 使用 `CallbackQueryHandler` 处理服务器选择和命令执行
    application.add_handler(CallbackQueryHandler(handle_server_selection))

    # 启动 bot
    application.run_polling()

if __name__ == '__main__':
    main()
