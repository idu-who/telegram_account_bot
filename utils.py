import arrow
import re
import os

import settings


def is_valid_username(username):
    return bool(re.match(r'\w{5,32}', username))


def is_valid_service_name(service):
    return bool(re.match(r'[a-z\d\-\+]+$', service))


def readable_service_name(service):
    service_name = service.replace('-', ' ')
    return service_name.title()


def save_credentials_file(service, document):
    service_dir = settings.BOT_FILES_PATH / service

    if not os.path.exists(service_dir):
        os.mkdir(service_dir)

    curr_time_ist = arrow.now('Asia/Kolkata').format('YYYY-MM-DD_HH:mm:ss')
    file_name = f'{service}_{curr_time_ist}.txt'
    file_path = service_dir / file_name
    document.get_file().download(file_path)

    return file_path
