from mongo_client import client


def is_admin(user_id):
    users = client.bot.users
    user = users.find_one({'_id': user_id})

    if user and user['role'] == 'admin':
        return True

    return False


def user_exists(user_id):
    users = client.bot.users
    user = users.find_one({'_id': user_id})

    if user:
        return True

    return False
