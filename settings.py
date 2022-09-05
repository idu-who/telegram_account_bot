import os
import pathlib

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CONNECTION_STRING = os.getenv('CONNECTION_STRING')
DEFAULT_LIMIT = 10
BOT_FILES_PATH = pathlib.Path('./bot_files')


class Services:
    SERVICES_FILE_NAME = BOT_FILES_PATH / 'services.txt'

    @classmethod
    def get(cls):
        with open(cls.SERVICES_FILE_NAME) as services_file:
            return [service.strip('\n') for service
                    in services_file.readlines()]

    @classmethod
    def add(cls, service_name):
        with open(cls.SERVICES_FILE_NAME, 'a') as services_file:
            services_file.write(service_name+'\n')

    @classmethod
    def remove(cls, service_name):
        services = []
        with open(cls.SERVICES_FILE_NAME, 'r') as services_file:
            services = services_file.readlines()

        with open(cls.SERVICES_FILE_NAME, 'w') as services_file:
            for service in services:
                if service.strip('\n') != service_name:
                    services_file.write(service)
