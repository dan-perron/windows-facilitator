import pyautogui
import time
import logging
import os
import cv2
import numpy as np
from PIL import Image
import datetime
from .commish_config import CommishHomeCheckboxConfig
import pyscreeze
import shutil
from datetime import datetime, timedelta
from agent.backup import BackupManager
from agent.debug import DebugScreenshotManager
from agent.ui.checkbox import CheckboxInteractor
import threading
import hashlib
from agent.slack_notifier import SlackNotifier
from agent.ootp_screenshot_monitor import OOTPScreenshotMonitor
from agent.pyautogui_utils import (
    get_window_screenshot, get_window, locate_on_screen,
    click_at, click_center, set_textbox_value
)
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
logger.info(f"Images directory: {IMAGES_DIR}")

DEBUG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'debug')
os.makedirs(DEBUG_DIR, exist_ok=True)

MAX_DEBUG_SCREENSHOTS = 100

# Set up managers
slack_notifier = SlackNotifier()
debug_manager = DebugScreenshotManager(DEBUG_DIR, slack_notifier=slack_notifier)
backup_manager = BackupManager()
checkbox_interactor = CheckboxInteractor(os.path.join(IMAGES_DIR, 'commish_home_checkboxes'), debug_manager)

def find_and_click(image_name, confidence=0.75, timeout=10, verify_click=True):
    image_path = os.path.join(IMAGES_DIR, image_name)
    logger.info(f"Attempting to click image: {image_name}")
    if not os.path.exists(image_path):
        logger.warning(f"Image file does not exist: {image_path}")
        return False
    try:
        ref_img_pil = Image.open(image_path).convert("RGB")
    except Exception as e:
        logger.error(f"Error loading image {image_name}: {str(e)}")
        return False
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            screenshot = get_window_screenshot()
            if screenshot is None:
                time.sleep(0.5)
                continue
            location = locate_on_screen(ref_img_pil, confidence=confidence)
            if location:
                center = click_center(location)
                if center:
                    # Save debug screenshot with red dot at click location
                    try:
                        debug_screenshot = get_window_screenshot()
                        if debug_screenshot is not None:
                            debug_manager.save(
                                debug_screenshot, center.x, center.y,
                                label=image_name, action="click",
                                slack_message=f"Clicked {image_name} at ({center.x}, {center.y})"
                            )
                    except Exception as e:
                        logger.warning(f"Failed to save debug click image: {e}")
                    logger.info(f"Clicked image: {image_name} at ({center.x}, {center.y})")
                    return True
        except Exception as e:
            logger.error(f"Error attempting to click {image_name}: {str(e)}")
            break
        time.sleep(0.5)
    logger.warning(f"Image not found on screen for click: {image_name} (confidence: {confidence})")
    return False

CHECKBOX_IMAGE_MAP = {
    'backup_league_files': 'backup_league_files',
    'retrieve_team_exports_from_server': 'retrieve_team_exports_from_server',
    'retrieve_team_exports_from_your_pc': 'retrieve_team_exports_from_your_pc',
    'break_if_team_files_are_missing': 'break_if_team_files_are_missing',
    'break_if_trades_are_pending': 'break_if_trades_are_pending',
    'demote_release_players_with_dfa_time_left_of_x_days_or_less': 'demote_release_players_with_dfa_time_left_of_x_days_or_less',
    'auto_play_days': 'auto_play_days',
    'create_and_upload_league_file': 'create_and_upload_league_file',
    'create_and_upload_html_reports': 'create_and_upload_html_reports',
    'create_sql_dump_for_ms_access': 'create_sql_dump_for_ms_access',
    'create_sql_dump_for_mysql': 'create_sql_dump_for_mysql',
    'export_data_to_csv_files': 'export_data_to_csv_files',
    'upload_status_report_to_server': 'upload_status_report_to_server',
    'create_and_send_result_emails': 'create_and_send_result_emails',
}

CHECKBOX_IMAGE_DIR = os.path.join(IMAGES_DIR, 'commish_home_checkboxes')

def get_template_match_confidence(screenshot, template_path):
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        return None, 0.0
    screenshot_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return max_loc, max_val  # max_val is the confidence

def save_debug_click_screenshot(x, y, label=None, action=None):
    screenshot = get_window_screenshot()
    if screenshot is not None:
        debug_img = screenshot.copy()
        from PIL import ImageDraw
        draw = ImageDraw.Draw(debug_img)
        r = 10
        draw.ellipse((x - r, y - r, x + r, y + r), fill='red', outline='red')
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        action_str = f"_{action}" if action else ""
        label_str = f"_{label}" if label else ""
        debug_filename = os.path.join(DEBUG_DIR, f"{timestamp}{label_str}{action_str}_click_debug.png")
        debug_img.save(debug_filename)
        logger.info(f"Saved debug click image: {debug_filename}")
        # Retention policy: keep only the last MAX_DEBUG_SCREENSHOTS
        debug_files = sorted([f for f in os.listdir(DEBUG_DIR) if f.endswith('_click_debug.png')])
        if len(debug_files) > MAX_DEBUG_SCREENSHOTS:
            for f in debug_files[:-MAX_DEBUG_SCREENSHOTS]:
                try:
                    os.remove(os.path.join(DEBUG_DIR, f))
                    logger.info(f"Removed old debug screenshot: {f}")
                except Exception as e:
                    logger.warning(f"Failed to remove old debug screenshot {f}: {e}")

def set_commish_home_checkboxes(config: CommishHomeCheckboxConfig, confidence=0.95, timeout=8):
    screenshot = get_window_screenshot()
    if screenshot is None:
        error_msg = "Failed to get window screenshot"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
        
    for attr, base_name in CHECKBOX_IMAGE_MAP.items():
        desired = getattr(config, attr)
        try:
            checkbox_interactor.set_checkbox_state(screenshot, attr, base_name, desired)
        except RuntimeError as e:
            # Re-raise with more context
            raise RuntimeError(f"Failed to set checkbox state for {attr}: {str(e)}") from e
        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"Unexpected error setting checkbox state for {attr}: {str(e)}") from e

def set_textbox_relative_to_checkbox(checkbox_image, x_offset, y_offset, value, confidence=0.85):
    location = locate_on_screen(checkbox_image, confidence=confidence)
    if location:
        center = click_center(location)
        if center:
            textbox_pos = (center.x + x_offset, center.y + y_offset)
            logger.info(f"Clicking form field at {textbox_pos} (relative to anchor {checkbox_image}) and setting value '{value}'")
            set_textbox_value(textbox_pos, value)
            screenshot = get_window_screenshot()
            debug_manager.save(
                screenshot, textbox_pos[0], textbox_pos[1],
                label="form_field", action=f"set_{value}",
                slack_message=f"Set textbox at {textbox_pos} to value '{value}' (anchor: {checkbox_image})"
            )
    else:
        logger.warning(f"Checkbox image not found for textbox anchor: {checkbox_image}")

def click_and_verify_next(image_name, next_image_name, max_retries=3, confidence=0.75):
    """
    Attempts to click an image and verify the next expected image is visible.
    Returns True if successful, False if all retries failed.
    """
    for attempt in range(max_retries):
        if find_and_click(image_name):
            time.sleep(2)
            if locate_on_screen(os.path.join(IMAGES_DIR, next_image_name), confidence=confidence):
                logger.info(f"Successfully verified {image_name} click - {next_image_name} is visible")
                return True
            else:
                logger.warning(f"{image_name} click attempt {attempt + 1}/{max_retries} - {next_image_name} not visible")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        if attempt == max_retries - 1:
            logger.error(f"Failed to verify {image_name} click after {max_retries} attempts")
            return False
    return False

def click_and_verify_screen_change(image_name, max_retries=3, confidence=0.75, change_threshold=0.1):
    """
    Attempts to click an image and verify the screen has changed.
    Returns True if successful, False if all retries failed.
    
    Args:
        image_name: Name of the image to click
        max_retries: Number of retry attempts
        confidence: Confidence level for image matching
        change_threshold: Minimum amount of screen change required (0-1)
    """
    for attempt in range(max_retries):
        # Take screenshot before click
        before_screenshot = get_window_screenshot()
        if before_screenshot is None:
            logger.warning(f"Could not get screenshot before click attempt {attempt + 1}")
            continue

        if find_and_click(image_name):
            time.sleep(2)  # Wait for screen to update
            
            # Take screenshot after click
            after_screenshot = get_window_screenshot()
            if after_screenshot is None:
                logger.warning(f"Could not get screenshot after click attempt {attempt + 1}")
                continue

            # Convert screenshots to numpy arrays for comparison
            before_array = np.array(before_screenshot)
            after_array = np.array(after_screenshot)

            # Calculate difference
            diff = np.mean(np.abs(before_array.astype(float) - after_array.astype(float)))
            change_percentage = diff / 255.0  # Normalize to 0-1 range

            if change_percentage > change_threshold:
                logger.info(f"Successfully verified {image_name} click - screen changed by {change_percentage:.2%}")
                return True
            else:
                logger.warning(f"{image_name} click attempt {attempt + 1}/{max_retries} - screen change too small ({change_percentage:.2%})")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue

        if attempt == max_retries - 1:
            logger.error(f"Failed to verify {image_name} click after {max_retries} attempts")
            return False
    return False

def simulate_ootp_workflow(checkbox_config=None, manual_import_teams=False, backup_league_folder=False, dry_run=False):
    window, message = get_window()
    if window is None:
        error_msg = f"OOTP window not found at start of simulate_ootp_workflow: {message}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg, "details": "Could not find OOTP window"}, 404
    try:
        if backup_league_folder:
            backup_manager.backup_with_slack(slack_notifier)
        logger.info(f"manual_import_teams: {manual_import_teams}")
        logger.info(f"dry_run: {dry_run}")
        time.sleep(1)

        # Click Commish Home and verify Check Team Exports is visible
        if not click_and_verify_next("comish_home.png", "check_team_exports.png"):
            error_msg = "Could not verify Commish Home Page navigation"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg, "details": "Failed to navigate to Commish Home page"}, 404

        time.sleep(2)
        # Set checkboxes according to config
        if checkbox_config is None:
            checkbox_config = CommishHomeCheckboxConfig()
        try:
            set_commish_home_checkboxes(checkbox_config)
        except RuntimeError as e:
            error_msg = str(e)
            logger.error(error_msg)
            return {"status": "error", "message": "Failed to set checkbox states", "details": error_msg}, 400
        except Exception as e:
            error_msg = f"Unexpected error setting checkboxes: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": "Failed to set checkbox states", "details": error_msg}, 500

        time.sleep(1)
        # Set DFA days textbox (anchor: demote_release_players_with_dfa_time_left_of_x_days_or_less)
        set_textbox_relative_to_checkbox(
            os.path.join(CHECKBOX_IMAGE_DIR, 'demote_release_players_with_dfa_time_left_of_x_days_or_less_unchecked.png'),
            x_offset=550, y_offset=0, value=checkbox_config.dfa_days_value
        )
        # Set Auto-play days textbox (anchor: auto_play_days)
        set_textbox_relative_to_checkbox(
            os.path.join(CHECKBOX_IMAGE_DIR, 'auto_play_days_unchecked.png'),
            x_offset=550, y_offset=0, value=checkbox_config.auto_play_days_value
        )
        time.sleep(1)

        if manual_import_teams:
            # Click Check Team Exports and verify Import All Teams is visible
            if not click_and_verify_next("check_team_exports.png", "import_all_teams.png"):
                error_msg = "Could not verify Check Team Exports navigation"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg, "details": "Failed to navigate to Check Team Exports page"}, 404

            # Click Import All Teams and verify Start Download is visible
            if not click_and_verify_next("import_all_teams.png", "start_download.png"):
                error_msg = "Could not verify Import All Teams navigation"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg, "details": "Failed to navigate to Import All Teams page"}, 404

            # Click Start Download and verify Cancel is visible
            if not click_and_verify_next("start_download.png", "cancel.png"):
                error_msg = "Could not verify Start Download navigation"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg, "details": "Failed to navigate to Start Download page"}, 404

            logger.info("Waiting for download to complete (up to 60 seconds)...")
            time.sleep(60)

            # Click Cancel and verify Commish Home is visible
            if not click_and_verify_next("cancel.png", "comish_home.png"):
                error_msg = "Could not verify Cancel navigation"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg, "details": "Failed to navigate back to Commish Home page"}, 404

            # Click Commish Home again and verify Execute is visible
            if not click_and_verify_next("comish_home.png", "execute.png"):
                error_msg = "Could not verify Commish Home navigation"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg, "details": "Failed to navigate to final Commish Home page"}, 404

        # Final step: click the 'execute' button and verify screen changes
        if not dry_run:
            if not click_and_verify_screen_change("execute.png"):
                error_msg = "Could not verify Execute button click"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg, "details": "Failed to execute the final action"}, 404
            return {"status": "success", "message": "Simulation completed"}, 200
        else:
            return {"status": "success", "message": "Dry run completed - all steps verified but execute button not clicked"}, 200
    except Exception as e:
        error_message = f"Error during simulation: {str(e)}"
        error_type = f"Exception type: {type(e)}"
        error_trace = traceback.format_exc()
        logger.error(error_message)
        logger.error(error_type)
        logger.error("Traceback:\n" + error_trace)
        # Send error to Slack
        slack_notifier.send_message(
            f"*Simulation Error:*\n"
            f"{error_message}\n{error_type}\n```{error_trace}```"
        )
        return {
            "status": "error",
            "message": error_message,
            "details": f"{error_type}\n{error_trace}"
        }, 500 

def check_ootp_window():
    """
    Checks if the OOTP window exists and is active.
    Returns a tuple of (success, message) where success is a boolean.
    """
    window, message = get_window()
    return window is not None, message 