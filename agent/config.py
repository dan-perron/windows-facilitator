import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from config.env
config_path = Path(__file__).parent.parent / 'config.env'
load_dotenv(config_path)

# Backup Configuration
BACKUP_SOURCE = os.getenv('BACKUP_SOURCE')
BACKUP_ROOT = os.path.expanduser(os.getenv('BACKUP_ROOT', '~/Documents/ootp_backups'))
BACKUP_DAILY_LIMIT = int(os.getenv('BACKUP_DAILY_LIMIT', '30'))
BACKUP_WEEKLY_LIMIT = int(os.getenv('BACKUP_WEEKLY_LIMIT', '13'))

# Slack Configuration
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_CHANNEL = os.getenv('SLACK_CHANNEL') 