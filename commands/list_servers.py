from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.db import Database
from utils.logging import bot_logger

db = Database()

async def list_servers(update: Update, context: CallbackContext) -> None:
    try:
        servers = db.get_servers(update.effective_user.id)
        
        if not servers:
            await update.message.reply_text("没有已添加的服务器。")
            return

        selected_servers = context.user_data.get('selected_servers', [])

        # 构建服务器选择按钮
        keyboard = []
        for s in servers:
            alias = s[2]
            if alias in selected_servers:
                keyboard.append([InlineKeyboardButton(f"✔️ {alias}", callback_data=alias)])
            else:
                keyboard.append([InlineKeyboardButton(alias, callback_data=alias)])
        
        # 添加取消选择和执行命令按钮
        keyboard.append([InlineKeyboardButton("取消选择", callback_data="cancel_selection")])
        keyboard.append([InlineKeyboardButton("执行命令", callback_data="execute_command")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("请选择服务器（可以多选）:", reply_markup=reply_markup)
        bot_logger.info(f"用户 {update.effective_user.id} 列出了服务器。")
    except Exception as e:
        bot_logger.error(f"列出服务器出错: {str(e)}")
        await update.message.reply_text(f"列出服务器失败: {str(e)}")

async def handle_server_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    selected_servers = context.user_data.get('selected_servers', [])

    if query.data == "cancel_selection":
        context.user_data.pop('selected_servers', None)
        await query.edit_message_text(text="已取消选择。")
    elif query.data == "execute_command":
        if not selected_servers:
            await query.edit_message_text(text="未选择任何服务器。")
        else:
            await query.edit_message_text(text=f"已选择的服务器: {', '.join(selected_servers)}\n正在执行命令...")
            # 在这里调用执行命令的逻辑
            await execute_on_selected_servers(update, context)
    else:
        # 处理服务器选择和反选
        if query.data in selected_servers:
            selected_servers.remove(query.data)
        else:
            selected_servers.append(query.data)
        context.user_data['selected_servers'] = selected_servers

        # 重新构建键盘以显示当前选择状态
        await list_servers(update, context)
