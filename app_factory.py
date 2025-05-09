import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

# Set up logging to file and console
LOG_DIR = os.path.join(os.path.expanduser('~'), 'Documents', 'ootp_logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'stdout.log')

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(name)s: %(message)s')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
console_handler.setFormatter(console_formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Load environment variables from config.env if present
    try:
        from dotenv import load_dotenv
        load_dotenv("config.env")
    except ImportError:
        pass

    # Register routes
    from controller import register_routes
    register_routes(app)

    return app

# For Flask CLI support
app = create_app() 