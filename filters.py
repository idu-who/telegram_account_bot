from telegram.ext import UpdateFilter

from db_operations import (
    is_admin,
    user_has_auth
)


class AuthorizedFilter(UpdateFilter):
    def filter(self, update):
        user = update.message.from_user
        return user_has_auth(user)


class AdminFilter(UpdateFilter):
    def filter(self, update):
        user = update.message.from_user
        return is_admin(user.id)
