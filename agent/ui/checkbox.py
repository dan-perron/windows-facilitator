import os
import cv2
import numpy as np
import time
import logging
from agent.debug import DebugScreenshotManager
from agent.pyautogui_utils import click_at

class CheckboxInteractor:
    def __init__(self, image_dir, debug_manager, confidence=0.95):
        self.image_dir = image_dir
        self.debug_manager = debug_manager
        self.confidence = confidence
        self.logger = logging.getLogger(__name__)

    def get_template_match_confidence(self, screenshot, template_path):
        if not os.path.exists(template_path):
            error_msg = f"Required image file not found: {template_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            error_msg = f"Failed to load image file: {template_path}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)
            
        screenshot_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        return max_loc, max_val, template.shape

    def set_checkbox_state(self, screenshot, attr, base_name, desired):
        checked_img = os.path.join(self.image_dir, f"{base_name}_checked.png")
        unchecked_img = os.path.join(self.image_dir, f"{base_name}_unchecked.png")

        try:
            checked_loc, checked_conf, checked_shape = self.get_template_match_confidence(screenshot, checked_img)
            unchecked_loc, unchecked_conf, unchecked_shape = self.get_template_match_confidence(screenshot, unchecked_img)
        except FileNotFoundError as e:
            self.logger.error(f"Missing required checkbox image for {attr}: {str(e)}")
            raise RuntimeError(f"Missing required checkbox image for {attr}. Please ensure both checked and unchecked versions exist.") from e
        except ValueError as e:
            self.logger.error(f"Failed to load checkbox image for {attr}: {str(e)}")
            raise RuntimeError(f"Failed to load checkbox image for {attr}. The image file may be corrupted.") from e

        if checked_conf > unchecked_conf and checked_conf >= self.confidence:
            current_state = 'checked'
            best_loc = checked_loc
            template_shape = checked_shape
        elif unchecked_conf > checked_conf and unchecked_conf >= self.confidence:
            current_state = 'unchecked'
            best_loc = unchecked_loc
            template_shape = unchecked_shape
        else:
            current_state = 'not found'
            best_loc = None
            template_shape = (0, 0)

        self.logger.info(f"Checkbox '{attr}': desired state = {'checked' if desired else 'unchecked'}, "
                         f"current state = {current_state} (checked_conf={checked_conf:.3f}, unchecked_conf={unchecked_conf:.3f})")

        if desired and current_state == 'unchecked' and best_loc:
            x, y = best_loc
            h, w = template_shape
            center_x = x + w // 2
            center_y = y + h // 2
            self.logger.info(f"Clicking to check '{attr}' at center ({center_x}, {center_y})")
            click_at(center_x, center_y)
            self.debug_manager.save(
                screenshot, center_x, center_y,
                label=f"{attr}_checked", action="check",
                slack_message=f"Checked '{attr}' at ({center_x}, {center_y})"
            )
            time.sleep(0.3)
        elif not desired and current_state == 'checked' and best_loc:
            x, y = best_loc
            h, w = template_shape
            center_x = x + w // 2
            center_y = y + h // 2
            self.logger.info(f"Clicking to uncheck '{attr}' at center ({center_x}, {center_y})")
            click_at(center_x, center_y)
            self.debug_manager.save(
                screenshot, center_x, center_y,
                label=f"{attr}_unchecked", action="uncheck",
                slack_message=f"Unchecked '{attr}' at ({center_x}, {center_y})"
            )
            time.sleep(0.3)
        elif current_state == 'not found':
            self.logger.warning(f"Could not find checkbox for {attr} (checked or unchecked)") 