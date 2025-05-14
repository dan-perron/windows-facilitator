import pyautogui
import time
import logging

def get_window(window_title="Out of the Park Baseball 25"):
    """
    Gets the specified window and ensures it's active.
    Returns a tuple of (window, message) where window is the window object or None if not found.
    """
    logger = logging.getLogger(__name__)
    try:
        window = pyautogui.getWindowsWithTitle(window_title)
        if not window:
            return None, f"Window '{window_title}' not found"
        window = window[0]
        if not window.isActive:
            window.activate()
            time.sleep(0.5)
        return window, f"Window '{window_title}' found and active"
    except Exception as e:
        logger.error(f"Error getting window: {str(e)}")
        return None, f"Error getting window: {str(e)}"

def get_window_screenshot(window_title="Out of the Park Baseball 25"):
    logger = logging.getLogger(__name__)
    try:
        window, message = get_window(window_title)
        if window is None:
            logger.error(message)
            return None
        region = (window.left, window.top, window.width, window.height)
        screenshot = pyautogui.screenshot(region=region)
        return screenshot
    except Exception as e:
        logger.error(f"Error getting window screenshot: {str(e)}")
        return None 