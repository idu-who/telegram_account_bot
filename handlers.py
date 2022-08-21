from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters
)

from callbacks.common_callbacks import (
    start,
    unknown
)

from callbacks.admin_callbacks import (
    help_admin
)

from callbacks.user_callbacks import (
    help_user
)

import settings

# common command handlers
start_handler = CommandHandler('start', start)
unknown_handler = MessageHandler(Filters.all, unknown)

# admin command handlers
help_admin_handler = CommandHandler(
    'help',
    help_admin,
    Filters.user(settings.admin_user_id)
)

# user command handlers
help_user_handler = CommandHandler(
    'help',
    help_user,
    ~Filters.user(settings.admin_user_id)
)
