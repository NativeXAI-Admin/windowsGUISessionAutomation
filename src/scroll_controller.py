"""
Scroll Controller - Mouse Wheel Based Scrolling
Handles all page navigation using ONLY mouse wheel events (NO keyboard).

CRITICAL: This module NEVER uses keyboard input - only mouse wheel scrolling.
"""

import time
import json
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

import pyautogui
import numpy as np
from PIL import Image
from loguru import logger


class ScrollDirection(Enum):
    """Scroll direction enum"""
    UP = "up"
    DOWN = "down"


@dataclass
class ScrollPosition:
    """Track current scroll position"""
    total_distance: int = 0
    scroll_count: int = 0
    last_screenshot_hash: Optional[str] = None
    is_at_bottom: bool = False


class ScrollController:
    """
    Mouse Wheel Scroll Controller
    
    Responsibilities:
    - Scroll pages using ONLY mouse wheel events
    - Detect when reaching end of infinite scroll pages
    - Track scroll position for recovery
    - Coordinate scrolling with screenshot capture
    - Handle both finite and infinite scroll scenarios
    
    CRITICAL: Uses pyautogui.scroll() which triggers mouse wheel events,
    NOT keyboard events like Page Down or arrow keys.
    """
    
    def __init__(self, config_path: str = "config/scroll_settings.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
        # Scroll settings
        self.step_size = self.config.get('scroll', {}).get('step_size', 800)
        self.wait_after_scroll = self.config.get('scroll', {}).get('wait_after_scroll', 1.5)
        self.max_scrolls = self.config.get('scroll', {}).get('max_scrolls_per_page', 10)
        
        # Mouse wheel settings
        self.scroll_clicks = self.config.get('mouse_wheel', {}).get('scroll_down_clicks', -3)
        
        # Position tracking
        self.position = ScrollPosition()
        
        # End-of-page detection
        self.end_detection_threshold = self.config.get('scroll', {}).get('detection', {}).get('end_of_page_threshold', 3)
        self.similarity_threshold = self.config.get('scroll', {}).get('detection', {}).get('similarity_threshold', 0.95)
        self.consecutive_same_screenshots = 0
        
        logger.info("Scroll Controller initialized")
    
    def load_config(self) -> dict:
        """Load scroll configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    logger.info("Scroll config loaded")
                    return config
            else:
                logger.warning(f"Config not found: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading scroll config: {e}")
            return {}
    
    def scroll_down(self, clicks: Optional[int] = None) -> bool:
        """
        Scroll down using mouse wheel
        
        Args:
            clicks: Number of mouse wheel clicks (negative = down)
                   If None, uses default from config
        
        Returns:
            True if scroll successful
        """
        try:
            if clicks is None:
                clicks = self.scroll_clicks
            
            # Use pyautogui.scroll() - this sends mouse wheel events, NOT keyboard
            pyautogui.scroll(clicks)
            
            # Update position tracking
            self.position.scroll_count += 1
            self.position.total_distance += abs(clicks * 100)  # Approximate pixels
            
            # Wait for content to load
            time.sleep(self.wait_after_scroll)
            
            logger.debug(f"Scrolled down ({clicks} clicks)")
            return True
            
        except Exception as e:
            logger.error(f"Error scrolling down: {e}")
            return False
    
    def scroll_up(self, clicks: Optional[int] = None) -> bool:
        """
        Scroll up using mouse wheel
        
        Args:
            clicks: Number of mouse wheel clicks (positive = up)
        
        Returns:
            True if scroll successful
        """
        try:
            if clicks is None:
                clicks = abs(self.scroll_clicks)  # Positive for up
            
            pyautogui.scroll(clicks)
            
            self.position.scroll_count += 1
            self.position.total_distance -= abs(clicks * 100)
            
            time.sleep(self.wait_after_scroll)
            
            logger.debug(f"Scrolled up ({clicks} clicks)")
            return True
            
        except Exception as e:
            logger.error(f"Error scrolling up: {e}")
            return False
    
    def scroll_to_top(self) -> bool:
        """
        Scroll to top of page using repeated upward scrolls
        
        Returns:
            True if successful
        """
        try:
            logger.info("Scrolling to top...")
            
            # Scroll up aggressively
            for _ in range(20):  # Should be enough for most pages
                self.scroll_up(clicks=10)
                time.sleep(0.3)
            
            # Reset position
            self.position = ScrollPosition()
            
            logger.success("Scrolled to top")
            return True
            
        except Exception as e:
            logger.error(f"Error scrolling to top: {e}")
            return False
    
    def scroll_step(self) -> bool:
        """
        Scroll one step down (configured step size)
        
        Returns:
            True if scrolled, False if at bottom
        """
        if self.position.is_at_bottom:
            logger.debug("Already at bottom")
            return False
        
        return self.scroll_down()
    
    def detect_end_of_page(self, screenshot: Optional[Image.Image] = None) -> bool:
        """
        Detect if we've reached the end of an infinite scroll page
        
        Strategy:
        - Take screenshots after each scroll
        - Compare with previous screenshot
        - If content identical for N consecutive scrolls, we're at the end
        
        Args:
            screenshot: PIL Image to compare (if None, takes new screenshot)
        
        Returns:
            True if at end of page
        """
        try:
            if screenshot is None:
                screenshot = pyautogui.screenshot()
            
            # Convert to hash for comparison
            img_hash = self._image_hash(screenshot)
            
            # Compare with previous
            if self.position.last_screenshot_hash == img_hash:
                self.consecutive_same_screenshots += 1
                logger.debug(f"Same screenshot detected ({self.consecutive_same_screenshots}/{self.end_detection_threshold})")
            else:
                self.consecutive_same_screenshots = 0
            
            # Update last hash
            self.position.last_screenshot_hash = img_hash
            
            # Check if we've hit the threshold
            if self.consecutive_same_screenshots >= self.end_detection_threshold:
                self.position.is_at_bottom = True
                logger.info("End of page detected")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting end of page: {e}")
            return False
    
    def _image_hash(self, image: Image.Image) -> str:
        """
        Generate simple hash of image for comparison
        
        Args:
            image: PIL Image
        
        Returns:
            Hash string
        """
        try:
            # Resize to small size for faster comparison
            small = image.resize((64, 64))
            
            # Convert to grayscale
            gray = small.convert('L')
            
            # Get pixel data
            pixels = np.array(gray)
            
            # Simple hash: average pixel value
            avg = np.mean(pixels)
            
            # Create hash from average (simple but effective)
            return f"{avg:.2f}"
            
        except Exception as e:
            logger.error(f"Error hashing image: {e}")
            return str(time.time())  # Fallback to timestamp
    
    def scroll_and_capture(
        self,
        capture_callback,
        max_scrolls: Optional[int] = None
    ) -> List:
        """
        Scroll down and capture screenshots at each step
        
        Args:
            capture_callback: Function to call after each scroll (receives screenshot)
            max_scrolls: Maximum number of scrolls (None = use config)
        
        Returns:
            List of results from capture_callback
        """
        if max_scrolls is None:
            max_scrolls = self.max_scrolls
        
        results = []
        
        logger.info(f"Starting scroll and capture (max {max_scrolls} scrolls)")
        
        for i in range(max_scrolls):
            # Take screenshot before scrolling
            screenshot = pyautogui.screenshot()
            
            # Check if at end
            if self.detect_end_of_page(screenshot):
                logger.info(f"Reached end after {i} scrolls")
                break
            
            # Call capture callback
            try:
                result = capture_callback(screenshot, i)
                if result is not None:
                    results.append(result)
            except Exception as e:
                logger.error(f"Capture callback error: {e}")
            
            # Scroll down
            if not self.scroll_down():
                logger.warning("Scroll failed, stopping")
                break
            
            logger.debug(f"Scroll {i+1}/{max_scrolls} complete")
        
        logger.success(f"Scroll and capture complete: {len(results)} results")
        return results
    
    def reset(self):
        """Reset scroll position tracking"""
        self.position = ScrollPosition()
        self.consecutive_same_screenshots = 0
        logger.debug("Scroll position reset")
    
    def get_position(self) -> ScrollPosition:
        """Get current scroll position"""
        return self.position
    
    def smooth_scroll_down(self, distance: int = 800) -> bool:
        """
        Smooth scroll down a specific pixel distance
        
        Args:
            distance: Pixels to scroll down
        
        Returns:
            True if successful
        """
        try:
            # Calculate number of small scrolls needed
            clicks_per_step = 1
            steps = abs(distance) // 100
            
            for _ in range(steps):
                pyautogui.scroll(-clicks_per_step)
                time.sleep(0.05)  # Small delay for smoothness
            
            # Wait for final load
            time.sleep(self.wait_after_scroll)
            
            logger.debug(f"Smooth scrolled {distance}px")
            return True
            
        except Exception as e:
            logger.error(f"Error in smooth scroll: {e}")
            return False


class RedditScrollController(ScrollController):
    """
    Specialized scroll controller for Reddit's infinite scroll
    """
    
    def __init__(self, config_path: str = "config/scroll_settings.json"):
        super().__init__(config_path)
        
        # Reddit-specific settings
        reddit_config = self.config.get('reddit_specific', {})
        self.posts_per_scroll = reddit_config.get('posts_per_scroll', 3)
        self.max_posts = reddit_config.get('max_posts_to_capture', 30)
        self.wait_for_load = reddit_config.get('wait_for_load', 2.0)
        
        logger.info("Reddit Scroll Controller initialized")
    
    def scroll_to_post(self, post_index: int) -> bool:
        """
        Scroll to approximately the Nth post
        
        Args:
            post_index: Target post number (0-based)
        
        Returns:
            True if successful
        """
        try:
            # Estimate scrolls needed
            scrolls_needed = post_index // self.posts_per_scroll
            
            # Reset to top first
            self.scroll_to_top()
            
            # Scroll down to target
            for _ in range(scrolls_needed):
                self.scroll_down()
            
            logger.info(f"Scrolled to approximately post {post_index}")
            return True
            
        except Exception as e:
            logger.error(f"Error scrolling to post: {e}")
            return False


if __name__ == "__main__":
    # Test scroll controller
    from loguru import logger
    logger.add("logs/scroll_test.log", rotation="10 MB")
    
    print("=" * 60)
    print("SCROLL CONTROLLER TEST")
    print("=" * 60)
    
    controller = ScrollController()
    
    print(f"✓ Config loaded: {bool(controller.config)}")
    print(f"✓ Step size: {controller.step_size}px")
    print(f"✓ Max scrolls: {controller.max_scrolls}")
    
    print("\nTesting scroll down...")
    controller.scroll_down()
    print(f"✓ Scroll count: {controller.position.scroll_count}")
    
    print("\nTesting scroll to top...")
    controller.scroll_to_top()
    print(f"✓ Position reset: {controller.position.scroll_count == 0}")
    
    print("\n✓ Test complete!")
    print("=" * 60)
