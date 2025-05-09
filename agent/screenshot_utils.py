import pyautogui
import time
import logging

def get_window_screenshot(window_title="Out of the Park Baseball 25"):
    logger = logging.getLogger(__name__)
    try:
        window = pyautogui.getWindowsWithTitle(window_title)
        if not window:
            logger.error(f"Could not find window: {window_title}")
            return None
        window = window[0]
        if not window.isActive:
            window.activate()
            time.sleep(0.5)
        region = (window.left, window.top, window.width, window.height)
        screenshot = pyautogui.screenshot(region=region)
        return screenshot
    except Exception as e:
        logger.error(f"Error getting window screenshot: {str(e)}")
        return None 