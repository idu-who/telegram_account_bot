from telegram.ext import UpdateFilter

from utils import user_has_auth


class AuthorizedFilter(UpdateFilter):
    def filter(self, update):
        user = update.message.from_user
        return user_has_auth(user)
