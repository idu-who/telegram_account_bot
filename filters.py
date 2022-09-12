from telegram.ext import UpdateFilter

from utils.db_operations import Users


class AuthorizedFilter(UpdateFilter):
    def filter(self, update):
        message = update.message or update.edited_message
        user = message.from_user
        return Users.is_authorized(user)


class AdminFilter(UpdateFilter):
    def filter(self, update):
        user = update.message.from_user
        return Users.is_admin(user)
