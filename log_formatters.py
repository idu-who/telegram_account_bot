import logging
import pytz

from datetime import datetime

import settings


class TzAwareFormatter(logging.Formatter):
    """override logging.Formatter to use an timezone aware datetime object."""

    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        local_tz = pytz.timezone(settings.IST_TIMEZONE)
        return dt.astimezone(local_tz)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s
