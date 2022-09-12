import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CONNECTION_STRING = os.getenv('CONNECTION_STRING')
DEFAULT_LIMIT = 10
UPLOAD_PATH = Path('./uploads')
LOGS_FILE_NAME = 'bot.log'
USER_TIMEZONE = 'Asia/Kolkata'
RESET_TIME = '17:00'  # hour, minutes
