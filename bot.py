import logging

from telegram.ext import Updater

import settings

from handlers import (
    start_handler,
    help_handler,
    unknown_handler
)

updater = Updater(
    token=settings.BOT_TOKEN,
    use_context=True
)
dispatcher = updater.dispatcher

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
# if no handlers are invoked, use unknown_handler
dispatcher.add_handler(unknown_handler)

updater.start_polling()
