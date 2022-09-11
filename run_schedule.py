import threading
import time

from datetime import datetime, timedelta
from pytz import timezone

import schedule

import settings


def seconds_until_next_hour():
    now = datetime.now(timezone(settings.USER_TIMEZONE))
    curr_hour = now.replace(minute=0, second=0, microsecond=0)
    next_hour = curr_hour + timedelta(minutes=60)
    remaining_time = next_hour - now

    return remaining_time.total_seconds()


def run_continuously():
    """Run scheduled jobs continously."""
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                interval = seconds_until_next_hour()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run
