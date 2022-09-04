from pprint import pprint

from telegram import (
    Update,
    ParseMode
)

from telegram.ext import CallbackContext

from mongo_client import client
from utils import (
    is_admin,
    get_admin_username,
    user_exists_by_telegram_user_id,
    user_exists_by_username,
    user_has_auth,
    is_valid_user,
    is_valid_username
)


def start(update: Update, context: CallbackContext):
    """For starting the bot."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(f'Hi {update.message.from_user.full_name}.'
              '\nUse /help to view all commands.')
    )


def help_menu(update: Update, context: CallbackContext):
    """For showing help menu."""
    menu_text = ("Here's a list of available commands:\n"
                 "/help \- view this help menu\.")

    if is_admin(update.message.from_user.id):
        menu_text += ("\n\n*Admin Commands:*\n"
                      "/adduser \- add a new user\.\n"
                      "/removeuser \- remove an existing user\.")

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


def unauthorized(update: Update, context: CallbackContext):
    """For unauthorized users."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Sorry, you don't have access to this bot."
              f"\nContact @{get_admin_username()} to purchase a"
              " subscription.")
    )


def add_user(update: Update, context: CallbackContext):
    """For adding new users."""
    if context.args:
        username = context.args[0].lstrip('@')

        if is_valid_username(username):
            if not user_exists_by_username(username):
                user_document = {
                    'username': username,
                    'role': 'reseller'
                }
                client.bot.users.insert_one(user_document)
                response_message = f'User @{username} added.'
            else:
                response_message = (f'User with username @{username} already'
                                    ' exists.')
        else:
            response_message = f'Username @{username} is invalid.'
    else:
        response_message = '/adduser requires a username.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_message
    )


def remove_user(update: Update, context: CallbackContext):
    """For removing users."""
    if context.args:
        username = context.args[0].lstrip('@')

        if is_valid_username(username):
            if user_exists_by_username(username):
                client.bot.users.delete_one({'username': username})
                response_message = f'User @{username} removed.'
            else:
                response_message = (f'User with username @{username} does not'
                                    ' exists.')
        else:
            response_message = f'Username @{username} is invalid.'
    else:
        response_message = '/removeuser requires a username.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_message
    )
