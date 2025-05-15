import pyautogui
import time
import logging
import os
from PIL import Image

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

def locate_on_screen(image, confidence=0.75):
    """
    Locates an image on the screen.
    Args:
        image: PIL Image or path to image file
        confidence: Confidence level for image matching (0-1)
    Returns:
        Location object if found, None otherwise
    """
    try:
        if isinstance(image, str):
            if not os.path.exists(image):
                logger.error(f"Image file does not exist: {image}")
                return None
            image = Image.open(image).convert("RGB")
        return pyautogui.locateOnScreen(image, confidence=confidence)
    except Exception as e:
        logger.error(f"Error locating image on screen: {str(e)}")
        return None

def click_at(x, y, duration=0.5):
    """
    Clicks at the specified coordinates.
    Args:
        x: X coordinate
        y: Y coordinate
        duration: Duration of the click in seconds
    """
    try:
        pyautogui.moveTo(x, y)
        time.sleep(0.1)
        pyautogui.click(duration=duration)
    except Exception as e:
        logger.error(f"Error clicking at ({x}, {y}): {str(e)}")

def click_center(location, duration=0.5):
    """
    Clicks at the center of a location.
    Args:
        location: Location object from locate_on_screen
        duration: Duration of the click in seconds
    """
    try:
        center = pyautogui.center(location)
        click_at(center.x, center.y, duration)
        return center
    except Exception as e:
        logger.error(f"Error clicking center of location: {str(e)}")
        return None

def set_textbox_value(textbox_pos, value):
    """
    Sets the value of a textbox at the specified position.
    Args:
        textbox_pos: (x, y) tuple of textbox position
        value: Value to set
    """
    try:
        click_at(textbox_pos[0], textbox_pos[1])
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        pyautogui.write(str(value))
        time.sleep(0.2)
    except Exception as e:
        logger.error(f"Error setting textbox value: {str(e)}")

# Configure logging
logger = logging.getLogger(__name__) 