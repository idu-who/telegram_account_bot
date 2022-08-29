from telegram import (
    Update,
    ParseMode
)

from telegram.ext import CallbackContext

from utils import (
    is_admin
)


def start(update: Update, context: CallbackContext):
    start_text = (f'Hi {update.message.from_user.full_name}.'
                  '\nUse /help to view all commands.')
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=start_text
    )


def help_menu(update: Update, context: CallbackContext):
    menu_text = ("Here's a list of available commands:\n"
                 "/help \- view this help menu\.")

    if is_admin(update.message.from_user.id):
        menu_text += ("\n\n*Admin Commands:*\n"
                      "/adduser \- add a new user\.\n"
                      "/removeuser \- remove an existing user\.\n"
                      "/searchusers \- search existing users by name\.")

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=menu_text,
        parse_mode=ParseMode.MARKDOWN_V2
    )


def unknown(update: Update, context: CallbackContext):
    """For unknown messages."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Sorry, I didn\'t understand that.'
    )
