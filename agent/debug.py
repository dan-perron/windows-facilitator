import os
import logging
from datetime import datetime
from PIL import ImageDraw
from agent.slack_notifier import SlackNotifier

class DebugScreenshotManager:
    def __init__(self, debug_dir, max_screenshots=100, slack_notifier=None):
        self.debug_dir = debug_dir
        self.max_screenshots = max_screenshots
        self.logger = logging.getLogger(__name__)
        os.makedirs(self.debug_dir, exist_ok=True)
        self.slack_notifier = slack_notifier

    def save(self, screenshot, x, y, label=None, action=None, slack_message=None):
        debug_img = screenshot.copy()
        draw = ImageDraw.Draw(debug_img)
        r = 10
        draw.ellipse((x - r, y - r, x + r, y + r), fill='red', outline='red')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        action_str = f"_{action}" if action else ""
        label_str = f"_{label}" if label else ""
        debug_filename = os.path.join(self.debug_dir, f"{timestamp}{label_str}{action_str}_click_debug.png")
        debug_img.save(debug_filename)
        self.logger.info(f"Saved debug click image: {debug_filename}")
        # Retention policy: keep only the last max_screenshots
        debug_files = sorted([f for f in os.listdir(self.debug_dir) if f.endswith('_click_debug.png')])
        if len(debug_files) > self.max_screenshots:
            for f in debug_files[:-self.max_screenshots]:
                try:
                    os.remove(os.path.join(self.debug_dir, f))
                    self.logger.info(f"Removed old debug screenshot: {f}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove old debug screenshot {f}: {e}")
        if slack_message and self.slack_notifier:
            self.slack_notifier.send_file(debug_filename, slack_message)

    # _send_to_slack is no longer needed, handled by SlackNotifier 