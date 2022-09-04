from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters
)

from callbacks import (
    start,
    help_menu,
    unknown,
    unauthorized,
    add_user,
    remove_user
)
from filters import AuthorizedFilter

authorized_filter = AuthorizedFilter()

# common command handlers
start_handler = CommandHandler('start', start, filters=authorized_filter)
help_handler = CommandHandler('help', help_menu, filters=authorized_filter)
unknown_handler = MessageHandler(Filters.all & authorized_filter, unknown)
unauthorized_handler = MessageHandler(Filters.all, unauthorized)

# admin command handlers
add_user_handler = CommandHandler('adduser', add_user)
remove_user_handler = CommandHandler('removeuser', remove_user)

# user command handlers
