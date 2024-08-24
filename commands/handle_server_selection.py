from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from commands.cancel_selection import cancel_selection
from utils.db import Database
from commands.execute_on_selected_servers import execute_on_selected_servers  # 导入执行命令函数

db = Database()

async def handle_server_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    selected_servers = context.user_data.get('selected_servers', [])

    if query.data == "cancel_selection":
        await cancel_selection(update, context)
    elif query.data == "execute_command":
        if not selected_servers:
            await query.edit_message_text(text="未选择任何服务器。")
        else:
            await query.edit_message_text(text=f"已选择的服务器: {', '.join(selected_servers)}\n正在执行命令...")
            await execute_on_selected_servers(update, context)
    else:
        # 处理服务器选择和反选
        if query.data in selected_servers:
            selected_servers.remove(query.data)
        else:
            selected_servers.append(query.data)
        context.user_data['selected_servers'] = selected_servers

        # 重新构建键盘以显示当前选择状态
        await update_server_selection_message(query, context, selected_servers)

async def update_server_selection_message(query, context, selected_servers):
    servers = db.get_servers(query.from_user.id)
    keyboard = []

    for server in servers:
        alias = server[2]
        if alias in selected_servers:
            keyboard.append([InlineKeyboardButton(f"✔️ {alias}", callback_data=alias)])
        else:
            keyboard.append([InlineKeyboardButton(alias, callback_data=alias)])

    keyboard.append([InlineKeyboardButton("取消选择", callback_data="cancel_selection")])
    keyboard.append([InlineKeyboardButton("执行命令", callback_data="execute_command")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"当前已选择的服务器: {', '.join(selected_servers)}", reply_markup=reply_markup)
