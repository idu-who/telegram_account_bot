from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters
)

from callbacks import (
    start,
    help_menu,
    services,
    show_usage,
    unknown,
    unauthorized,
    add_user,
    remove_user,
    set_limits,
    edit_limit,
    add_service,
    remove_service,
    cancel
)
from filters import AuthorizedFilter, AdminFilter

authorized_filter = AuthorizedFilter()
admin_filter = AdminFilter()

# common command handlers
start_handler = CommandHandler('start', start, filters=authorized_filter)
help_handler = CommandHandler('help', help_menu, filters=authorized_filter)
services_handler = CommandHandler(
    'services',
    services,
    filters=authorized_filter
)
show_usage_handler = CommandHandler(
    'showusage',
    show_usage,
    filters=authorized_filter
)
cancel_handler = CommandHandler('cancel', cancel, filters=authorized_filter)
unknown_handler = MessageHandler(Filters.all & authorized_filter, unknown)
unauthorized_handler = MessageHandler(Filters.all, unauthorized)

# admin command handlers
add_user_handler = CommandHandler(
    'adduser',
    add_user,
    filters=authorized_filter & admin_filter
)
remove_user_handler = CommandHandler(
    'removeuser',
    remove_user,
    filters=authorized_filter & admin_filter
)
set_limits_handler = CommandHandler(
    'setlimits',
    set_limits,
    filters=authorized_filter & admin_filter
)
edit_limit_handler = CommandHandler(
    'editlimit',
    edit_limit,
    filters=authorized_filter & admin_filter
)
set_limits_conversation_handler = ConversationHandler(
    entry_points=[set_limits_handler],
    states={
        0: [edit_limit_handler]
    },
    fallbacks=[cancel_handler, unknown_handler]
)
add_service_handler = CommandHandler(
    'addservice',
    add_service,
    filters=authorized_filter & admin_filter
)
remove_service_handler = CommandHandler(
    'removeservice',
    remove_service,
    filters=authorized_filter & admin_filter
)
# user command handlers
