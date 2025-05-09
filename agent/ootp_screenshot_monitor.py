import pyautogui
import threading
import hashlib
import logging
from datetime import datetime

class OOTPScreenshotMonitor:
    def __init__(self, debug_manager, window_title="Out of the Park Baseball 25", interval=10):
        self.debug_manager = debug_manager
        self.window_title = window_title
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = None
        self._last_hash = None
        self.logger = logging.getLogger(__name__)

    def _get_window_screenshot(self):
        try:
            window = pyautogui.getWindowsWithTitle(self.window_title)
            if not window:
                return None
            window = window[0]
            if not window.isActive:
                return None
            region = (window.left, window.top, window.width, window.height)
            screenshot = pyautogui.screenshot(region=region)
            return screenshot
        except Exception as e:
            self.logger.error(f"Monitor: Error getting window screenshot: {str(e)}")
            return None

    def _screenshot_hash(self, screenshot):
        import io
        buf = io.BytesIO()
        screenshot.save(buf, format='PNG')
        return hashlib.md5(buf.getvalue()).hexdigest()

    def _send_to_slack(self, screenshot):
        if self.debug_manager.slack_notifier:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                screenshot.save(tmp.name)
                tmp.flush()
                self.debug_manager.slack_notifier.send_file(
                    tmp.name,
                    f"OOTP window changed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )

    def _monitor_loop(self):
        self.logger.info("OOTPScreenshotMonitor started.")
        while not self._stop_event.is_set():
            screenshot = self._get_window_screenshot()
            if screenshot is not None:
                current_hash = self._screenshot_hash(screenshot)
                if self._last_hash != current_hash:
                    self._send_to_slack(screenshot)
                    self._last_hash = current_hash
            self._stop_event.wait(self.interval)
        self.logger.info("OOTPScreenshotMonitor stopped.")

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join() 