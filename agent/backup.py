import os
import shutil
from datetime import datetime
import logging
from agent.slack_notifier import SlackNotifier

class BackupManager:
    def __init__(self, source, backup_root, daily_limit=30, weekly_limit=13):
        self.source = source
        self.backup_root = backup_root
        self.daily_limit = daily_limit
        self.weekly_limit = weekly_limit
        self.logger = logging.getLogger(__name__)
        os.makedirs(self.backup_root, exist_ok=True)

    def backup(self):
        now = datetime.now()
        daily_name = now.strftime('daily_%Y%m%d_%H%M%S')
        daily_backup_path = os.path.join(self.backup_root, daily_name)
        shutil.copytree(self.source, daily_backup_path)
        self.logger.info(f"League files backed up to {daily_backup_path}")
        self.prune_backups()
        self.weekly_backup(now)

    def prune_backups(self):
        daily_backups = sorted([d for d in os.listdir(self.backup_root) if d.startswith('daily_')])
        if len(daily_backups) > self.daily_limit:
            for d in daily_backups[:-self.daily_limit]:
                shutil.rmtree(os.path.join(self.backup_root, d), ignore_errors=True)
                self.logger.info(f"Removed old daily backup: {d}")

    def weekly_backup(self, now):
        week_num = now.strftime('%Y%W')
        weekly_name = f'weekly_{week_num}'
        weekly_backup_path = os.path.join(self.backup_root, weekly_name)
        if not os.path.exists(weekly_backup_path):
            shutil.copytree(self.source, weekly_backup_path)
            self.logger.info(f"League files weekly backup to {weekly_backup_path}")
        weekly_backups = sorted([d for d in os.listdir(self.backup_root) if d.startswith('weekly_')])
        if len(weekly_backups) > self.weekly_limit:
            for d in weekly_backups[:-self.weekly_limit]:
                shutil.rmtree(os.path.join(self.backup_root, d), ignore_errors=True)
                self.logger.info(f"Removed old weekly backup: {d}")

    def backup_with_slack(self, slack_notifier):
        slack_notifier.send_message(f"Starting league files backup from {self.source} to {self.backup_root}")
        self.backup()
        # Find the latest daily backup path
        daily_backups = sorted([d for d in os.listdir(self.backup_root) if d.startswith('daily_')])
        if daily_backups:
            latest_daily = os.path.join(self.backup_root, daily_backups[-1])
        else:
            latest_daily = None
        slack_notifier.send_message(f"League files backup complete. Latest daily: {latest_daily}")
        return latest_daily 