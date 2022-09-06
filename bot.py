import logging

from telegram.ext import Updater

import settings

from handlers import (
    start_handler,
    help_handler,
    services_handler,
    show_usage_handler,
    fetch_handler,
    unknown_handler,
    unauthorized_handler,
    add_user_handler,
    remove_user_handler,
    set_limits_conversation_handler,
    add_service_handler,
    remove_service_handler,
    upload_handler
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
dispatcher.add_handler(services_handler)
dispatcher.add_handler(show_usage_handler)
dispatcher.add_handler(fetch_handler)
dispatcher.add_handler(add_user_handler)
dispatcher.add_handler(remove_user_handler)
dispatcher.add_handler(set_limits_conversation_handler)
dispatcher.add_handler(add_service_handler)
dispatcher.add_handler(remove_service_handler)
dispatcher.add_handler(upload_handler)
# if no handlers are invoked for authorized user use unknown_handler
# and for unauthorized use unauthorized_handler
dispatcher.add_handler(unknown_handler)
dispatcher.add_handler(unauthorized_handler)

updater.start_polling()
# updater.idle()
