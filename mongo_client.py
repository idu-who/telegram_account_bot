import pymongo

import settings

server_api = pymongo.server_api.ServerApi('1')
client = pymongo.MongoClient(settings.CONNECTION_STRING, server_api=server_api)
