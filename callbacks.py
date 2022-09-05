from telegram import (
    Update,
    ParseMode
)

from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

import settings

from db_operations import (
    is_admin,
    user_exists_by_telegram_user_id,
    user_exists_by_username,
    get_or_create_limit
)
from mongo_client import client
from utils import (
    is_valid_username,
    is_valid_service_name,
    readable_service_name
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
                 "/help \- view this help menu\.\n"
                 "/services \- list all services\.\n"
                 "/showusage \- show service usage and limit\.")

    if is_admin(update.message.from_user.id):
        menu_text += ("\n\n*Admin Commands:*\n"
                      "/adduser \<username\> \- add a new user\.\n"
                      "/removeuser \<username\> \- remove an existing user\.\n"
                      "/setlimits \<username\> \- set limits for a user\.\n"
                      "/addservice \<service\> \- add a new service\.\n"
                      "/removeservice \<service\> \- remove an existing service\.")

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=menu_text,
        parse_mode=ParseMode.MARKDOWN_V2
    )


def services(update: Update, context: CallbackContext):
    """For listing all available services."""
    service_list_text = '\n'.join([
        f"{readable_service_name(service):15} \- {service:>15}"
        for service in settings.Services.get()
    ])
    services_text = ("Here's a list of available services:\n"
                     f"`{service_list_text}`")
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=services_text,
        parse_mode=ParseMode.MARKDOWN_V2
    )


def show_usage(update: Update, context: CallbackContext):
    """For displaying used and total limits of user."""
    user = update.message.from_user
    user_document = user_exists_by_telegram_user_id(user.id)
    limit_document = get_or_create_limit(user_document)
    del limit_document['_id']
    usage_list_text = '\n'.join([
        f'| {readable_service_name(service):16}|{0:>5} |{quota:>6} |'
        for service, quota in limit_document.items()
    ])
    usage_text = ('`|     Service     | Used | Total |\n'
                  '----------------------------------\n'
                  f'{usage_list_text}`')
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=usage_text,
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
    admin_username = client.bot.users.find_one({'role': 'admin'})['username']
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Sorry, you don't have access to this bot."
              f"\nContact @{admin_username} to purchase a"
              " subscription.")
    )


def add_user(update: Update, context: CallbackContext):
    """For adding a new user."""
    if context.args:
        username = context.args[0].lstrip('@')

        if is_valid_username(username):
            if not user_exists_by_username(username):
                user_document = {
                    'username': username,
                    'role': 'reseller'
                }
                client.bot.users.insert_one(user_document)
                add_user_response = f'User @{username} added.'
            else:
                add_user_response = (f'User with username @{username} has'
                                     ' already been added.')
        else:
            add_user_response = f'Username @{username} is invalid.'
    else:
        add_user_response = '/adduser requires a username.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=add_user_response
    )


def remove_user(update: Update, context: CallbackContext):
    """For removing an existing user."""
    if context.args:
        username = context.args[0].lstrip('@')

        if is_valid_username(username):
            user_document = user_exists_by_username(username)
            if user_document:
                client.bot.users.delete_one({'_id': user_document['_id']})
                client.bot.limits.delete_one({'_id': user_document['_id']})
                remove_user_response = f'User @{username} removed.'
            else:
                remove_user_response = (f'User with username @{username} does'
                                        ' not exists.')
        else:
            remove_user_response = f'Username @{username} is invalid.'
    else:
        remove_user_response = '/removeuser requires a username.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=remove_user_response
    )


def set_limits(update: Update, context: CallbackContext):
    """For setting the limits of a user."""
    if context.args:
        username = context.args[0].lstrip('@')

        if is_valid_username(username):
            user_document = user_exists_by_username(username)
            if user_document:
                context.chat_data['user_document'] = user_document

                limit_document = get_or_create_limit(user_document)
                del limit_document['_id']
                limit_list_text = '\n'.join([
                    f'{readable_service_name(service):15} \- {quota:>3}'
                    for service, quota in limit_document.items()
                ])
                set_limits_text = (f"Limits for @{username}:\n\n"
                                   f'`{limit_list_text}`\n\n'
                                   'Use /editlimit \<service\> \<new\-limit\>'
                                   ' to edit limits\.\n'
                                   'And /services to list all services\.\n'
                                   'And /cancel to exit /setlimits\.')
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=set_limits_text,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                return 0
            else:
                set_limits_response = (f'User with username @{username} does'
                                       ' not exists.')
        else:
            set_limits_response = f'Username @{username} is invalid.'
    else:
        set_limits_response = '/setlimits requires a username.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=set_limits_response,
    )
    return ConversationHandler.END


def edit_limit(update: Update, context: CallbackContext):
    """For editing a limit."""
    edit_limit_response = []

    if len(context.args) >= 2:
        service = context.args[0].lower()
        new_limit = context.args[1]

        if service not in settings.Services.get():
            edit_limit_response = [f'{service} is not a service.']
        if not (new_limit.isdigit() and int(new_limit) >= 0):
            edit_limit_response += [f'{new_limit} is not a valid'
                                    ' limit value.']

        if not edit_limit_response:
            user_document = context.chat_data['user_document']
            limits = client.bot.limits
            new_data = {service: int(new_limit)}
            limits.update_one(
                {'_id': user_document['_id']},
                {'$set': new_data}
            )

            limit_document = limits.find_one({'_id': user_document['_id']})
            del limit_document['_id']
            limit_list_text = '\n'.join([
                f'{readable_service_name(_service):15} \- {quota:>3}*'
                if _service == service else
                f'{readable_service_name(_service):15} \- {quota:>3}'
                for _service, quota in limit_document.items()
            ])
            edit_limit_text = (f"Limits for @{user_document['username']}:\n\n"
                               f'`{limit_list_text}`\n\n'
                               'Use /editlimit \<service\> \<new\-limit\>'
                               ' to edit limits\.\n'
                               'And /services to list all services\.\n'
                               'And /cancel to exit /setlimits\.')
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=edit_limit_text,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return 0
    else:
        edit_limit_response = ['/editlimit requires service and new'
                               ' limit value.']

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='\n'.join(edit_limit_response)
    )


def add_service(update: Update, context: CallbackContext):
    """For adding a new service."""
    if context.args:
        service = context.args[0].lower()

        if is_valid_service_name(service):
            if service not in settings.Services.get():
                settings.Services.add(service)
                limits = client.bot.limits
                limits.update_many(
                    {},
                    {
                        '$set': {
                            service: settings.DEFAULT_LIMIT
                        }
                    }
                )
                add_service_response = f'Service {service} added.'
            else:
                add_service_response = (f'Service with name {service} already'
                                        ' exists.')
        else:
            add_service_response += f'{service} is not a valid service name.'
    else:
        add_service_response = '/addservice requires a service name.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=add_service_response
    )


def remove_service(update: Update, context: CallbackContext):
    """For removing an existing service."""
    if context.args:
        service = context.args[0].lower()

        if is_valid_service_name(service):
            if service in settings.Services.get():
                settings.Services.remove(service)
                limits = client.bot.limits
                limits.update_many(
                    {},
                    {
                        '$unset': {
                            service: ''
                        }
                    }
                )
                remove_service_response = f'Service {service} removed.'
            else:
                remove_service_response = (f'Service with name {service} does'
                                           ' not exist.')
        else:
            remove_service_response = f'{service} is not a valid service name.'
    else:
        remove_service_response = '/removeservice requires a service name.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=remove_service_response
    )


def cancel(update: Update, context: CallbackContext):
    context.chat_data.pop('user_document', None)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Process exited.'
    )
    return ConversationHandler.END
