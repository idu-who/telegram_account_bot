from telegram import Update
from telegram.ext import CallbackContext

# import settings


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Hi {update.message.from_user.full_name}.'
        '\nUse /help to view all commands.'
    )


def unknown(update: Update, context: CallbackContext):
    """For unknown messages."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Sorry, I didn\'t understand that.'
    )
