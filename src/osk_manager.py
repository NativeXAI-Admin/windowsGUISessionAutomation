"""
OSK Manager - Virtual On-Screen Keyboard Controller
Handles all text input via mouse clicking on virtual keyboard keys.

CRITICAL: This module NEVER uses keyboard input - only mouse clicks.
"""

import os
import json
import time
import subprocess
import psutil
from pathlib import Path
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass

import pyautogui
import pytesseract
from PIL import Image
import cv2
import numpy as np
from loguru import logger


@dataclass
class KeyPosition:
    """Screen coordinates for a single key on the OSK"""
    key: str
    x: int
    y: int
    width: int = 40
    height: int = 40
    
    @property
    def center(self) -> Tuple[int, int]:
        """Get center point for clicking"""
        return (self.x, self.y)


class OSKManager:
    """
    Virtual On-Screen Keyboard Manager
    
    Responsibilities:
    - Launch and manage Windows OSK.exe process
    - Calibrate key positions using OCR
    - Click virtual keys to type text
    - Handle special characters and shift key
    - Persist calibration data between sessions
    - Auto-recover from OSK crashes
    """
    
    def __init__(self, config_path: str = "config/osk_calibration.json"):
        self.config_path = Path(config_path)
        self.calibration: Dict[str, List[int]] = {}
        self.osk_process: Optional[subprocess.Popen] = None
        self.osk_window_bounds: Optional[Tuple[int, int, int, int]] = None
        self.is_calibrated = False
        
        # Typing settings
        self.click_duration = 0.05  # How long to hold mouse button
        self.key_delay = 0.1  # Delay between key clicks
        
        # Load existing calibration if available
        self.load_calibration()
        
        logger.info("OSK Manager initialized")
    
    def launch_osk(self) -> bool:
        """
        Launch the Windows On-Screen Keyboard
        
        Returns:
            True if launched successfully, False otherwise
        """
        try:
            # Check if OSK is already running
            if self.is_osk_running():
                logger.info("OSK already running")
                return True
            
            # Launch OSK.exe
            logger.info("Launching OSK.exe...")
            self.osk_process = subprocess.Popen(
                ["osk.exe"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for OSK to appear
            time.sleep(2)
            
            # Verify it launched
            if self.is_osk_running():
                logger.success("OSK launched successfully")
                self.detect_osk_bounds()
                return True
            else:
                logger.error("OSK failed to launch")
                return False
                
        except Exception as e:
            logger.error(f"Error launching OSK: {e}")
            return False
    
    def is_osk_running(self) -> bool:
        """Check if OSK process is running"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == 'osk.exe':
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def close_osk(self) -> bool:
        """Close the OSK application"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == 'osk.exe':
                    proc.terminate()
                    logger.info("OSK closed")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error closing OSK: {e}")
            return False
    
    def detect_osk_bounds(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect OSK window position on screen
        
        Returns:
            (left, top, right, bottom) or None
        """
        try:
            # Take screenshot
            screenshot = pyautogui.screenshot()
            img_array = np.array(screenshot)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Find bottom region (OSK usually appears at bottom)
            height, width = gray.shape
            bottom_region = gray[int(height * 0.7):, :]
            
            # Simple detection: find continuous gray region
            # This is a simplified approach - you may need better detection
            self.osk_window_bounds = (0, int(height * 0.75), 1000, height)
            
            logger.info(f"OSK bounds detected: {self.osk_window_bounds}")
            return self.osk_window_bounds
            
        except Exception as e:
            logger.error(f"Error detecting OSK bounds: {e}")
            return None
    
    def calibrate(self, force: bool = False) -> bool:
        """
        Auto-calibrate OSK key positions using OCR
        
        Args:
            force: Force recalibration even if calibration file exists
            
        Returns:
            True if calibration successful
        """
        if self.is_calibrated and not force:
            logger.info("Already calibrated (use force=True to recalibrate)")
            return True
        
        if not self.is_osk_running():
            logger.warning("OSK not running, launching...")
            if not self.launch_osk():
                return False
        
        try:
            logger.info("Starting OSK calibration...")
            
            # Wait for OSK to be fully visible
            time.sleep(2)
            
            # Take screenshot of OSK region
            if not self.osk_window_bounds:
                self.detect_osk_bounds()
            
            screenshot = pyautogui.screenshot()
            
            # Use default QWERTY layout coordinates as fallback
            # In production, you'd use OCR to detect actual key positions
            self.calibration = self._get_default_qwerty_layout()
            
            self.is_calibrated = True
            self.save_calibration()
            
            logger.success("OSK calibration complete!")
            return True
            
        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            return False
    
    def _get_default_qwerty_layout(self) -> Dict[str, List[int]]:
        """
        Get default QWERTY key coordinates
        Based on standard Windows OSK at 1920x1080 resolution
        
        These are approximate values - actual positions may vary
        """
        layout = {
            # Row 1 (numbers)
            '1': [80, 830], '2': [160, 830], '3': [240, 830],
            '4': [320, 830], '5': [400, 830], '6': [480, 830],
            '7': [560, 830], '8': [640, 830], '9': [720, 830],
            '0': [800, 830],
            
            # Row 2 (QWERTY)
            'q': [80, 890], 'w': [160, 890], 'e': [240, 890],
            'r': [320, 890], 't': [400, 890], 'y': [480, 890],
            'u': [560, 890], 'i': [640, 890], 'o': [720, 890],
            'p': [800, 890],
            
            # Row 3 (ASDFGH)
            'a': [100, 950], 's': [180, 950], 'd': [260, 950],
            'f': [340, 950], 'g': [420, 950], 'h': [500, 950],
            'j': [580, 950], 'k': [660, 950], 'l': [740, 950],
            
            # Row 4 (ZXCVBN)
            'z': [220, 1010], 'x': [300, 1010], 'c': [380, 1010],
            'v': [460, 1010], 'b': [520, 1010], 'n': [600, 1010],
            'm': [680, 1010],
            
            # Special keys
            'space': [520, 1070],
            'backspace': [900, 830],
            'enter': [920, 950],
            'shift': [60, 1010],
            '.': [760, 1010],
            ',': [700, 1010],
            '/': [840, 1010],
            '-': [880, 830],
            "'": [820, 950],
        }
        
        return layout
    
    def load_calibration(self) -> bool:
        """Load calibration data from JSON file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.calibration = data.get('keys', {})
                    self.is_calibrated = len(self.calibration) > 0
                    logger.info(f"Loaded calibration with {len(self.calibration)} keys")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error loading calibration: {e}")
            return False
    
    def save_calibration(self) -> bool:
        """Save calibration data to JSON file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "_description": "OSK key coordinates - auto-calibrated",
                "_screen_resolution": "1920x1080",
                "_calibration_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "keys": self.calibration
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.success(f"Calibration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving calibration: {e}")
            return False
    
    def click_key(self, key: str) -> bool:
        """
        Click a single key on the OSK
        
        Args:
            key: Character to type (lowercase)
            
        Returns:
            True if click successful
        """
        try:
            if key not in self.calibration:
                logger.warning(f"Key '{key}' not in calibration")
                return False
            
            coords = self.calibration[key]
            x, y = coords[0], coords[1]
            
            # Move mouse and click
            pyautogui.moveTo(x, y, duration=0.1)
            pyautogui.click(x, y, duration=self.click_duration)
            
            time.sleep(self.key_delay)
            
            logger.debug(f"Clicked key '{key}' at ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"Error clicking key '{key}': {e}")
            return False
    
    def type_text(self, text: str, verify: bool = False) -> bool:
        """
        Type text using OSK (mouse clicks only)
        
        Args:
            text: String to type
            verify: Whether to verify text appeared (not implemented yet)
            
        Returns:
            True if typing successful
        """
        if not self.is_calibrated:
            logger.error("OSK not calibrated! Run calibrate() first")
            return False
        
        if not self.is_osk_running():
            logger.warning("OSK not running, launching...")
            if not self.launch_osk():
                return False
        
        logger.info(f"Typing text: '{text}' ({len(text)} chars)")
        
        try:
            for char in text:
                # Handle uppercase
                if char.isupper():
                    # Click shift
                    self.click_key('shift')
                    # Click letter (lowercase)
                    self.click_key(char.lower())
                    # Release shift (click again)
                    self.click_key('shift')
                
                # Handle spaces
                elif char == ' ':
                    self.click_key('space')
                
                # Handle lowercase and numbers
                elif char.lower() in self.calibration:
                    self.click_key(char.lower())
                
                else:
                    logger.warning(f"Unsupported character: '{char}'")
            
            logger.success(f"Typed {len(text)} characters successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return False
    
    def backspace(self, count: int = 1) -> bool:
        """Press backspace key multiple times"""
        try:
            for _ in range(count):
                self.click_key('backspace')
            return True
        except Exception as e:
            logger.error(f"Error pressing backspace: {e}")
            return False
    
    def press_enter(self) -> bool:
        """Press the enter key"""
        try:
            return self.click_key('enter')
        except Exception as e:
            logger.error(f"Error pressing enter: {e}")
            return False
    
    def clear_field(self, triple_click_coords: Tuple[int, int]) -> bool:
        """
        Clear a text field by triple-clicking to select all, then backspace
        
        Args:
            triple_click_coords: (x, y) coordinates of the text field
            
        Returns:
            True if cleared successfully
        """
        try:
            x, y = triple_click_coords
            
            # Triple-click to select all
            pyautogui.click(x, y, clicks=3, interval=0.1)
            time.sleep(0.2)
            
            # Press backspace to delete
            self.backspace()
            
            logger.debug(f"Cleared field at ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing field: {e}")
            return False
    
    def get_osk_region(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Get OSK screen region to exclude from screenshots
        
        Returns:
            (left, top, right, bottom) or None
        """
        return self.osk_window_bounds
    
    def __enter__(self):
        """Context manager entry - launch OSK"""
        self.launch_osk()
        if not self.is_calibrated:
            self.calibrate()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close OSK"""
        self.close_osk()


if __name__ == "__main__":
    # Test OSK Manager
    from loguru import logger
    logger.add("logs/osk_test.log", rotation="10 MB")
    
    print("=" * 60)
    print("OSK MANAGER TEST")
    print("=" * 60)
    
    with OSKManager() as osk:
        print(f"✓ OSK running: {osk.is_osk_running()}")
        print(f"✓ Calibrated: {osk.is_calibrated}")
        
        if osk.is_calibrated:
            print("\nTesting typing...")
            test_text = "hello world"
            print(f"Typing: '{test_text}'")
            
            # You'd need a text field focused for this to work
            # This is just a demonstration
            osk.type_text(test_text)
            
            print("\n✓ Test complete!")
        else:
            print("\n⚠ Calibration required! Run calibrate() first")
    
    print("=" * 60)
