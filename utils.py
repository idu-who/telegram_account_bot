import re


def is_valid_username(username):
    return bool(re.match(r'\w{5,32}', username))


def is_valid_service_name(service):
    return bool(re.match(r'[a-z\d\-\+]+$', service))


def readable_service_name(service):
    service_name = service.replace('-', ' ')
    return service_name.title()
