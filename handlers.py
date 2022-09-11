import re

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters
)

from callbacks import (
    start,
    help_menu,
    services,
    usage,
    fetch_credentials,
    unknown,
    unauthorized,
    add_user,
    remove_user,
    edit_limit,
    add_service,
    remove_service,
    upload
)
from filters import AuthorizedFilter, AdminFilter

authorized_message_filter = Filters.update.message & AuthorizedFilter()
admin_message_filter = authorized_message_filter & AdminFilter()

# common command handlers
start_handler = CommandHandler(
    'start',
    start,
    filters=authorized_message_filter
)
help_handler = CommandHandler(
    'help',
    help_menu,
    filters=authorized_message_filter
)
services_handler = CommandHandler(
    'services',
    services,
    filters=authorized_message_filter
)
usage_handler = CommandHandler(
    'usage',
    usage,
    filters=authorized_message_filter
)
fetch_handler = CommandHandler(
    'fetch',
    fetch_credentials,
    filters=authorized_message_filter
)
unknown_handler = MessageHandler(Filters.all & AuthorizedFilter(), unknown)
unauthorized_handler = MessageHandler(Filters.all, unauthorized)

# admin command handlers
add_user_handler = CommandHandler(
    'adduser',
    add_user,
    filters=admin_message_filter
)
remove_user_handler = CommandHandler(
    'removeuser',
    remove_user,
    filters=admin_message_filter
)
edit_limit_handler = CommandHandler(
    'editlimit',
    edit_limit,
    filters=admin_message_filter
)
add_service_handler = CommandHandler(
    'addservice',
    add_service,
    filters=admin_message_filter
)
remove_service_handler = CommandHandler(
    'removeservice',
    remove_service,
    filters=admin_message_filter
)
upload_handler = MessageHandler(
    (admin_message_filter & Filters.document.txt &
     Filters.caption_regex(re.compile(r'^/upload', re.IGNORECASE))),
    upload
)
