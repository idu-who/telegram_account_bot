import logging

import schedule

from telegram.ext import Updater
from pytz import timezone

import settings
import run_schedule

from callbacks import error_callback
from datetime import datetime
from handlers import (
    start_handler,
    help_handler,
    services_handler,
    usage_handler,
    fetch_handler,
    unknown_handler,
    unauthorized_handler,
    add_user_handler,
    remove_user_handler,
    edit_limit_handler,
    add_service_handler,
    remove_service_handler,
    upload_handler
)
from log_formatters import TzAwareFormatter
from mongo_client import client

updater = Updater(
    token=settings.BOT_TOKEN,
    use_context=True
)
dispatcher = updater.dispatcher
dispatcher.add_error_handler(error_callback)

file_handler = logging.FileHandler(settings.LOGS_FILE_NAME)
file_handler.setFormatter(TzAwareFormatter(
    '\n%(asctime)s - %(filename)s:%(funcName)s:%(lineno)d'
    ' - %(name)s - %(levelname)s - %(message)s'
))
logging.basicConfig(
    handlers=[file_handler]
)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(services_handler)
dispatcher.add_handler(usage_handler)
dispatcher.add_handler(fetch_handler)
dispatcher.add_handler(add_user_handler)
dispatcher.add_handler(remove_user_handler)
dispatcher.add_handler(edit_limit_handler)
dispatcher.add_handler(add_service_handler)
dispatcher.add_handler(remove_service_handler)
dispatcher.add_handler(upload_handler)
# if no handlers are invoked for authorized user use unknown_handler
# and for unauthorized use unauthorized_handler
dispatcher.add_handler(unknown_handler)
dispatcher.add_handler(unauthorized_handler)

# convert reset_time from user timezone to system timezone
reset_hour, reset_minute = settings.RESET_TIME
system_timezone = datetime.now().replace(
    hour=reset_hour,
    minute=reset_minute
).astimezone().tzinfo
user_reset_time = datetime.now(timezone(settings.USER_TIMEZONE)).replace(
    hour=reset_hour,
    minute=reset_minute
)
system_reset_time = user_reset_time.astimezone(system_timezone)
reset_time_text = system_reset_time.strftime('%H:%M')


# cronjob to reset creds_used
def reset_creds_used():
    users = client.bot.users
    return users.update_many(
        {},
        {
            '$set': {
                'creds_used': 0
            }
        }
    )


schedule.every().day.at(reset_time_text).do(reset_creds_used)
stop_run_continuously = run_schedule.run_continuously(10)


updater.start_polling()
print('bot started')
updater.idle()
stop_run_continuously.is_set()
