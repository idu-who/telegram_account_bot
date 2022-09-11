import os

from datetime import datetime
from pytz import timezone
from re import match

import credential_parsers
import settings
from mongo_client import client


class Users:
    """For database operations related to the users collection."""
    users = client.bot.users

    @classmethod
    def add_user(cls, **kwargs):
        """Add new user with default values if not specified."""
        new_user_document = kwargs
        username = new_user_document.get('username')
        if username and cls.is_valid_username(username):
            new_user_document.setdefault('creds_used', 0)
            new_user_document.setdefault('limit', settings.DEFAULT_LIMIT)
            new_user_document.setdefault('role', 'reseller')

            return cls.users.insert_one(new_user_document)

    @classmethod
    def get_by_telegram_user_id(cls, telegram_user_id):
        """Returns user if exists, else returns None."""
        return cls.users.find_one({'telegram_user_id': telegram_user_id})

    @classmethod
    def get_by_username(cls, username):
        """Returns user if exists, else returns None."""
        return cls.users.find_one({'username': username})

    @classmethod
    def get_admin(cls):
        """Get the admin user."""
        return cls.users.find_one({'role': 'admin'})

    @classmethod
    def edit_limit_by_username(cls, username, new_limit):
        """Update user's limit."""
        return cls.users.update_one(
            {'username': username},
            {
                '$set': {
                    'limit': new_limit
                }
            }
        )

    @classmethod
    def edit_creds_used(cls, _id, new_creds_used_value):
        return cls.users.update_one(
            {'_id': _id},
            {
                '$set': {
                    'creds_used': new_creds_used_value
                }
            }
        )

    @classmethod
    def is_admin(cls, telegram_user):
        """Check if user belongs to admin role."""
        user_document = cls.get_by_telegram_user_id(
            telegram_user.id) or cls.get_by_username(telegram_user.username)

        if user_document and user_document.get('role') == 'admin':
            return True

        return False

    @classmethod
    def _update_details(cls, _id, telegram_user):
        """Update additional details of user."""
        new_user_details = {
            'telegram_user_id': telegram_user.id,
            'first_name': telegram_user.first_name,
            'last_name': telegram_user.last_name
        }
        return cls.users.update_one(
            {'_id': _id},
            {'$set': new_user_details}
        )

    @classmethod
    def is_authorized(cls, telegram_user):
        """Check if user is added telegram_user_id, else username.
        If username is added, update details."""
        if cls.get_by_telegram_user_id(telegram_user.id):
            return True
        else:
            user_document = cls.get_by_username(telegram_user.username)
            if user_document:
                cls._update_details(user_document['_id'], telegram_user)
                return True

        return False

    @classmethod
    def remove_by_username(cls, username):
        """Delete a user using username."""
        if username and cls.is_valid_username(username):
            return cls.users.delete_one({'username': username})

    @staticmethod
    def is_valid_username(username):
        """Check if username is valid."""
        return bool(match(r'[a-z\d_]{5,32}$', username))


class Services:
    """For database operations related to the services collection."""
    services = client.bot.services

    @classmethod
    def add_service(cls, service_name, **kwargs):
        """Add new service."""
        new_service_document = kwargs
        if service_name and cls.is_valid_service_name(service_name):
            new_service_document['name'] = service_name
            return cls.services.insert_one(new_service_document)

    @classmethod
    def get_service_by_name(cls, service_name):
        """Returns service if exists, else returns None."""
        return cls.services.find_one({'name': service_name})

    @classmethod
    def get_service_names(cls):
        """Get service names."""
        return [service_document.get('name')
                for service_document in cls.services.find()]

    @classmethod
    def remove_by_service_name(cls, service_name):
        """Delete a service using service name."""
        if service_name and cls.is_valid_service_name(service_name):
            return cls.services.delete_one({'name': service_name})

    @staticmethod
    def is_valid_service_name(service_name):
        """Check if a service name is valid."""
        return bool(match(r'[a-z\d\-\+]+$', service_name))

    @staticmethod
    def readable_service_name(service_name):
        """Get human readable service name."""
        return service_name.replace('-', ' ').title()


class Credentials:
    """For database operations related to the credentials collection."""
    credentials = client.bot.credentials

    @classmethod
    def add_credentials(cls, service_id, file_path, parser='BaseParser',
                        *args):
        """Parse credentials from a file and add them to database."""
        Parser = getattr(credential_parsers, parser)
        parsed_credentials = []
        with open(file_path) as credentials_file:
            for credential_text in credentials_file:
                parsed_credentials.append(
                    Parser.parse(credential_text, *args)
                )

        new_credential_documents = [
            {
                'service_id': service_id,
                'credential_data': parsed_credential
            }
            for parsed_credential in parsed_credentials
        ]

        return cls.credentials.insert_many(new_credential_documents)

    @classmethod
    def get_unused_credentials(cls, service_id, number_of_credentials=1):
        """Returns unused credentials if exists, else None"""
        return list(cls.credentials.find(
            {'service_id': service_id, 'used': None},
            limit=number_of_credentials
        ))

    @classmethod
    def set_credentials_used(cls, credential_documents, user_id):
        """Set credentials as used with used by and used at."""
        credential_ids = [credential_document['_id']
                          for credential_document in credential_documents]
        current_time = datetime.utcnow()
        return cls.credentials.update_many(
            {'_id': {'$in': credential_ids}},
            {
                '$set': {
                    'used': {
                        'by': user_id,
                        'at': current_time
                    }
                }
            }
        )

    @staticmethod
    def save_credentials_file(service_name, document):
        """Save uploaded credentials file in a service directory at
        UPLOAD_PATH."""
        service_dir = settings.UPLOAD_PATH / service_name

        if not os.path.exists(service_dir):
            os.mkdir(service_dir)

        curr_time_ist = datetime.now(
            timezone(settings.IST_TIMEZONE)
        ).isoformat()
        file_name = curr_time_ist + '.txt'
        file_path = service_dir / file_name
        document.get_file().download(file_path)

        return file_path
