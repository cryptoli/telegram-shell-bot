import configparser
from telegram import Update  # 确保导入了 Update 类
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
from commands.add_server import add_server
from commands.remove_server import remove_server
from commands.list_servers import list_servers
from commands.exec_command import exec_command
from commands.server_status import server_status
from commands.cancel_selection import cancel_selection

async def handle_server_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_selection":
        await cancel_selection(update, context)
    else:
        context.user_data['selected_server'] = query.data
        await query.edit_message_text(text=f"服务器 {query.data} 已选择")

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
    
    # 使用 `CallbackQueryHandler` 处理服务器选择
    application.add_handler(CallbackQueryHandler(handle_server_selection))

    # 启动 bot
    application.run_polling()

if __name__ == '__main__':
    main()
