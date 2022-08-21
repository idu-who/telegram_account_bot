from telegram import Update, ParseMode
from telegram.ext import CallbackContext

import settings


def help_admin(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=settings.admin_menu,
        parse_mode=ParseMode.MARKDOWN_V2
    )
