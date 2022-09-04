import re

from mongo_client import client


# database operation
def is_admin(user_id):
    users = client.bot.users
    user = users.find_one({'telegram_user_id': user_id})

    if user and user['role'] == 'admin':
        return True

    return False


def get_admin_username():
    users = client.bot.users
    admin_document = users.find_one({'role': 'admin'})
    return admin_document.get('username')


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


def is_valid_user(user_document):
    return bool(user_document.get('telegram_user_id') or
                user_document.get('username'))


def is_valid_username(username):
    return bool(re.match(r'\w{5,32}', username))
