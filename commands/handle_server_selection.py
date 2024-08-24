from telegram import Update
from telegram.ext import CallbackContext
from commands.cancel_selection import cancel_selection
from utils.db import Database

db = Database()

async def handle_server_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_selection":
        await cancel_selection(update, context)
    elif query.data == "execute_command":
        await execute_on_selected_servers(update, context)
    else:
        selected_servers = context.user_data.get('selected_servers', [])
        if query.data in selected_servers:
            selected_servers.remove(query.data)
        else:
            selected_servers.append(query.data)
        context.user_data['selected_servers'] = selected_servers
        await query.edit_message_text(text=f"当前已选择的服务器: {', '.join(selected_servers)}")
