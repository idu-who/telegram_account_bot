import logging

from telegram.ext import (
    Updater,
    PicklePersistence
)

import settings

from handlers import (
    unauthorized_handler,
    start_handler,
    help_handler,
    unknown_handler,
    add_user_handler,
    remove_user_handler
)

pickle_persistence = PicklePersistence(filename='persistence_file')

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
dispatcher.add_handler(add_user_handler)
dispatcher.add_handler(remove_user_handler)
# if no handlers are invoked for authorized user use unknown_handler
# and for unauthorized use unauthorized_handler
dispatcher.add_handler(unknown_handler)
dispatcher.add_handler(unauthorized_handler)

updater.start_polling()
