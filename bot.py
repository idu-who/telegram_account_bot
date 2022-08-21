import logging

from telegram.ext import Updater

from handlers import (
    start_handler,
    help_admin_handler,
    help_user_handler,
    unknown_handler
)

updater = Updater(
    token='5517306679:AAGPdtsgpGKJjCSRJGKHtXQHBh7tBH_ryw0',
    use_context=True
)
dispatcher = updater.dispatcher

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_admin_handler)
dispatcher.add_handler(help_user_handler)
# unknow if it does not match any command
dispatcher.add_handler(unknown_handler)

updater.start_polling()
