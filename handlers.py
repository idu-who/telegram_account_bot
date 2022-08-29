from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters
)

from callbacks import (
    start,
    help_menu,
    unknown
)

# common command handlers
start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help_menu)
unknown_handler = MessageHandler(Filters.all, unknown)

# admin command handlers

# user command handlers
