import configparser
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from commands.add_server import add_server
from commands.remove_server import remove_server
from commands.list_servers import list_servers
from commands.exec_command import exec_command
from commands.server_status import server_status
from commands.cancel_selection import cancel_selection

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
    application.add_handler(CallbackQueryHandler(lambda update, context: context.user_data.update(
        selected_server=update.callback_query.data) if update.callback_query.data != "cancel_selection" else cancel_selection(update, context)))

    # 启动 bot
    application.run_polling()

if __name__ == '__main__':
    main()
