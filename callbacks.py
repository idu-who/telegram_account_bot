import logging

from pymongo.errors import DuplicateKeyError
from telegram import (
    Update,
    ParseMode
)
from telegram.ext import (
    CallbackContext
)

from utils.db_operations import (
    Users,
    Services,
    Credentials
)


def error_callback(update: Update, context: CallbackContext):
    """For handling and logging errors."""
    error_message = None
    if update:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Sorry, there was an unexpected error.'
        )

        message_text = update.message.text or update.message.caption
        username = update.message.from_user.username
        error_message = ' - '.join(filter(None, [
            message_text,
            f'@{username}' if username else None
        ]))

    logging.error(
        error_message,
        exc_info=context.error,
        stack_info=False
    )


def start(update: Update, context: CallbackContext):
    """For starting the bot."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(f'Hi {update.message.from_user.full_name}.\n'
              'Use /help to view all commands.')
    )


def help_menu(update: Update, context: CallbackContext):
    """For showing help menu."""
    commands_list = [
        ('/help', 'view this help menu'),
        ('/services', 'list all services'),
        ('/usage', 'show usage info'),
        (
            '/fetch \\<_service_\\> \\[\\<_number\\-of\\-results_\\>\\]',
            'fetch credentials for a service'
        )
    ]
    commands_list_text = [f'{cmd} \\- {desc}\\.' for cmd, desc
                          in commands_list]
    commands_list_text.insert(0, "*Here's a list of available commands:*")
    response_text = '\n'.join(commands_list_text)

    if Users.is_admin(update.message.from_user):
        commands_list = [
            ('/adduser \\<_username_\\>', 'add a new user'),
            ('/removeuser \\<_username_\\>', 'remove a user'),
            ('/usage \\<_username_\\>', 'show usage info of a user'),
            (
                '/editlimit \\<_username_\\> \\<new\\-limit\\>',
                'edit limit for a user'
            ),
            ('/addservice \\<_service_\\>', 'add a new service'),
            ('/removeservice \\<_service_\\>', 'remove a service'),
            (
                '/upload \\<_service_\\>',
                'upload a credentials file with this command as caption'
            )
        ]
        commands_list_text = [f'{cmd} \\- {desc}\\.' for cmd, desc
                              in commands_list]
        commands_list_text.insert(0, "\n\n*Admin Commands:*")
        response_text += '\n'.join(commands_list_text)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text,
        parse_mode=ParseMode.MARKDOWN_V2
    )


def services(update: Update, context: CallbackContext):
    """For listing all available services."""
    services_list_text = '\n'.join([
        f"{Services.readable_service_name(service):15} \\- {service:>15}"
        for service in Services.get_service_names()
    ])
    response_text = ("Here's a list of available services:\n"
                     "`Name            \\-         Command\n`"
                     "`\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-"
                     "\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n`"
                     f"`{services_list_text}`")

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text,
        parse_mode=ParseMode.MARKDOWN_V2
    )


def usage(update: Update, context: CallbackContext):
    """For checking usage of a user."""
    response_text = ''
    user = update.message.from_user
    user_document = Users.get_by_telegram_user_id(user.id)

    if user_document['role'] == 'admin':
        if context.args:
            username = context.args[0].lstrip('@')
            if Users.is_valid_username(username):
                user_document = Users.get_by_username(username)
                if not user_document:
                    response_text = (f'User with username @{username} was not'
                                     ' found.')
            else:
                response_text = f'Username @{username} is invalid.'

    if not response_text:
        response_text = ('Usage info of user @{}.\n'
                         'Fetched {} credentials out of {} total.')
        response_text = response_text.format(
            user_document['username'],
            user_document['creds_used'],
            user_document['limit']
        )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text
    )


def fetch_credentials(update: Update, context: CallbackContext):
    """For fetching service credentials."""
    response_text = ''
    if context.args:
        service_name = context.args[0].lower()
        num_fetches = 1
        service_document = None

        if Services.is_valid_service_name(service_name):
            service_document = Services.get_service_by_name(service_name)
            if not service_document:
                response_text = (f'Service with name {service_name} was not'
                                 ' found.')
        else:
            response_text = f'Service name {service_name} is invalid.'

        if len(context.args) > 1:
            num_fetches = context.args[1]
            if not(num_fetches.isdigit() and int(num_fetches) > 0):
                sep = '\n' if response_text else ''
                response_text += (f'{sep}{num_fetches} is not a valid number'
                                  ' of results to fetch.')
            else:
                num_fetches = int(num_fetches)

        if not response_text:
            user = update.message.from_user
            user_document = Users.get_by_telegram_user_id(user.id)
            creds_used = user_document['creds_used']
            limit = user_document['limit']
            new_creds_used_value = creds_used + num_fetches

            if new_creds_used_value <= limit:
                fetched_credentials = Credentials.get_unused_credentials(
                    service_document['_id'],
                    num_fetches
                )
                actual_fetches = len(fetched_credentials)
                readable_service_name = Services.readable_service_name(
                    service_name)
                if actual_fetches > 0:
                    Credentials.set_credentials_used(
                        fetched_credentials,
                        user_document['_id']
                    )
                    Users.edit_creds_used(
                        user_document['_id'],
                        creds_used + actual_fetches
                    )
                    credential_data_list = [
                        fetched_credential['credential_data']
                        for fetched_credential in fetched_credentials
                    ]
                    response_text = ('Fetched {} credentials for {} service:\n'
                                     '`{}`')
                    response_text = response_text.format(
                        actual_fetches,
                        readable_service_name,
                        '\n'.join(credential_data_list)
                    )
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=response_text,
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
                    return
                else:
                    response_text = (f'Sorry, service {readable_service_name}'
                                     ' is out of stock.')
            else:
                response_text = (f"Can't fetch {num_fetches} credentials."
                                 ' Request exceeds limit.\n'
                                 'use /usage to check limit and usage.')
    else:
        response_text = '/fetch requires a service name.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text
    )


def unknown(update: Update, context: CallbackContext):
    """For unknown messages."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that."
    )


def unauthorized(update: Update, context: CallbackContext):
    """For unauthorized users."""
    admin_username = Users.get_admin()['username']

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Sorry, you don't have access to this bot.\n"
              f"Contact @{admin_username} to purchase a"
              " subscription.")
    )


def add_user(update: Update, context: CallbackContext):
    """For adding a new user."""
    if context.args:
        username = context.args[0].lstrip('@')

        try:
            insert_result = Users.add_user(username=username)
            if insert_result:
                response_text = f'User @{username} added.'
            else:
                response_text = f'Username @{username} is invalid.'
        except DuplicateKeyError:
            response_text = (f'User with username @{username} has already been'
                             ' added.')
    else:
        response_text = '/adduser requires a username.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text
    )


def remove_user(update: Update, context: CallbackContext):
    """For removing an existing user."""
    if context.args:
        username = context.args[0].lstrip('@')

        delete_result = Users.remove_by_username(username)
        if delete_result:
            if delete_result.deleted_count != 0:
                response_text = f'User @{username} removed.'
            else:
                response_text = (f'User with username @{username} was not'
                                 ' found.')
        else:
            response_text = f'Username @{username} is invalid.'

    else:
        response_text = '/removeuser requires a username.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text
    )


def edit_limit(update: Update, context: CallbackContext):
    """For editing a user's limit."""
    response_text = ''
    if len(context.args) >= 2:
        username = context.args[0].lstrip('@')
        new_limit = context.args[1]

        if not Users.is_valid_username(username):
            response_text = f'Username @{username} is invalid.'

        if not (new_limit.isdigit() and int(new_limit) >= 0):
            sep = '\n' if response_text else ''
            response_text += f'{sep}{new_limit} is not a valid limit value.'

        if not response_text:
            new_limit = int(new_limit)
            update_result = Users.edit_limit_by_username(username, new_limit)
            if update_result.matched_count != 0:
                response_text = f'Limit updated to {new_limit}.'
            else:
                response_text = (f'User with username @{username} was not'
                                 ' found.')
    else:
        response_text = ('/editlimit requires a username and a new'
                         ' limit value.')

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text
    )


def add_service(update: Update, context: CallbackContext):
    """For adding a new service."""
    # TODO: store parser and required args
    if context.args:
        service_name = context.args[0].lower()

        try:
            insert_result = Services.add_service(service_name)
            if insert_result:
                response_text = f'Service {service_name} added.'
            else:
                response_text = f'Service name {service_name} is invalid.'
        except DuplicateKeyError:
            response_text = (f'Service with name {service_name} has already'
                             ' been added.')
    else:
        response_text = '/addservice requires a service name.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text
    )


def remove_service(update: Update, context: CallbackContext):
    """For removing an existing service."""
    if context.args:
        service_name = context.args[0].lower()

        delete_result = Services.remove_by_service_name(service_name)
        if delete_result:
            if delete_result.deleted_count != 0:
                response_text = f'Service {service_name} removed.'
            else:
                response_text = (f'Service with name {service_name} was not'
                                 ' found.')
        else:
            response_text = f'Service name {service_name} is invalid.'
    else:
        response_text = '/removeservice requires a service name.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text
    )


def upload(update: Update, context: CallbackContext):
    """For storing an uploaded document."""
    # TODO: use service's own parser.
    caption_args = update.message.caption.split(' ')[1:]
    if caption_args:
        service_name = caption_args[0].lower()

        if Services.is_valid_service_name(service_name):
            service_document = Services.get_service_by_name(service_name)
            if service_document:
                file_path = Credentials.save_credentials_file(
                    service_name,
                    update.message.document
                )
                insert_result = Credentials.add_credentials(
                    service_document['_id'],
                    file_path
                )
                response_text = '{} credentials uploaded for {}.'
                response_text = response_text.format(
                    len(insert_result.inserted_ids),
                    Services.readable_service_name(
                        service_name)
                )
            else:
                response_text = (f'Service with name {service_name} was not'
                                 ' found.')
        else:
            response_text = f'Service name {service_name} is invalid.'
    else:
        response_text = '/upload requires a service name.'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text
    )
