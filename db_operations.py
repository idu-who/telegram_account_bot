import credential_parsers
import settings
from mongo_client import client


def is_admin(user_id):
    users = client.bot.users
    user = users.find_one({'telegram_user_id': user_id})

    if user and user['role'] == 'admin':
        return True

    return False


def user_exists_by_telegram_user_id(telegram_user_id):
    users = client.bot.users
    user_document = users.find_one({'telegram_user_id': telegram_user_id})

    if user_document:
        return user_document
    return False


def user_exists_by_username(username):
    users = client.bot.users
    user_document = users.find_one({'username': username})

    if user_document:
        return user_document
    return False


def _update_user_details(user_document, user):
    new_details = {
        'telegram_user_id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name
    }
    users = client.bot.users
    users.update_one(
        {'_id': user_document['_id']},
        {'$set': new_details}
    )


def user_has_auth(user):
    if user_exists_by_telegram_user_id(user.id):
        return True
    else:
        user_document = user_exists_by_username(user.username)
        if user_document:
            _update_user_details(user_document, user)
            return True
    return False


def get_or_create_limit(user_document):
    limits = client.bot.limits
    limit_document = limits.find_one({'_id': user_document['_id']})

    if not limit_document:
        limit_document = {
            service: settings.DEFAULT_LIMIT
            for service in settings.Services.get()
        }
        limit_document['_id'] = user_document['_id']
        limits.insert_one(limit_document)

    return limit_document


def save_credentials_db(service, file_path, parser, *args):
    print('file_path', file_path, 'parser', parser, 'args', args)
    credentials_list = []
    with open(file_path) as credentials_file:
        credentials_list = credentials_file.readlines()

    Parser = getattr(credential_parsers, parser or 'BaseParser')
    credentials_documents = [
        {
            'service': service,
            'credential_data': Parser.parse(credential, *args)
        }
        for credential in credentials_list
    ]
    credentials = client.bot.credentials
    credentials.insert_many(credentials_documents)


def get_or_update_credentials_used(user_document):
    credentials_used = user_document.get('credentials_used')
    if credentials_used:
        return credentials_used
    else:
        limit_document = get_or_create_limit(user_document)
        del limit_document['_id']
        users = client.bot.users
        users.update_one(
            {'_id': user_document['_id']},
            {
                '$set': {
                    'credentials_used': limit_document
                }
            }
        )
        return limit_document
