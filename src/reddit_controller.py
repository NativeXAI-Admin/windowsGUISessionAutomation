"""
Reddit Browser Controller - Mouse-Only Navigation
All browser automation using ONLY mouse clicks and OSK typing.

CRITICAL: This module NEVER uses keyboard input - only mouse clicks and OSK.
"""

import time
import json
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass

import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger

from osk_manager import OSKManager
from scroll_controller import RedditScrollController
from screenshot_engine import RedditScreenshotEngine


@dataclass
class RedditSearchResult:
    """Results from a Reddit search"""
    keyword: str
    tab: str  # "hot", "new", "top", "rising"
    posts_captured: int
    timestamp: str


class RedditBrowserController:
    """
    Reddit Browser Controller - Mouse and OSK Only
    
    Responsibilities:
    - Open browser and navigate to Reddit using OSK
    - Search for keywords using OSK typing
    - Click tabs (Hot/New/Top) using mouse
    - Manage browser state without keyboard shortcuts
    - Clear text fields using triple-click selection
    - Navigate between posts and comments
    
    CRITICAL: NO keyboard input - only mouse clicks and OSK typing
    """
    
    def __init__(
        self,
        osk_manager: OSKManager,
        scroll_controller: RedditScrollController,
        screenshot_engine: RedditScreenshotEngine,
        config_path: str = "config/screen_coordinates.json"
    ):
        self.osk = osk_manager
        self.scroller = scroll_controller
        self.screenshot = screenshot_engine
        
        # Load UI coordinates
        self.config_path = Path(config_path)
        self.coords = self.load_coordinates()
        
        # Browser instance
        self.driver: Optional[webdriver.Chrome] = None
        
        # Reddit URLs
        self.reddit_base = "https://www.reddit.com"
        self.reddit_search = f"{self.reddit_base}/search/"
        
        logger.info("Reddit Browser Controller initialized")
    
    def load_coordinates(self) -> dict:
        """Load screen coordinate configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    coords = json.load(f)
                    logger.info("Screen coordinates loaded")
                    return coords
            else:
                logger.warning(f"Coordinates file not found: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading coordinates: {e}")
            return {}
    
    def launch_browser(self, headless: bool = False) -> bool:
        """
        Launch Chrome browser
        
        Args:
            headless: Run in headless mode
        
        Returns:
            True if launched successfully
        """
        try:
            options = Options()
            
            if headless:
                options.add_argument('--headless')
            
            # Set window size
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            
            # Disable notifications
            options.add_argument('--disable-notifications')
            
            # Launch browser
            self.driver = webdriver.Chrome(options=options)
            
            logger.success("Browser launched")
            return True
            
        except Exception as e:
            logger.error(f"Error launching browser: {e}")
            return False
    
    def close_browser(self):
        """Close the browser"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    def navigate_to_url(self, url: str) -> bool:
        """
        Navigate to URL using OSK (NO keyboard)
        
        Steps:
        1. Click address bar
        2. Triple-click to select existing URL
        3. Type new URL using OSK
        4. Click Enter on OSK
        
        Args:
            url: URL to navigate to
        
        Returns:
            True if navigation successful
        """
        try:
            if not self.driver:
                logger.error("Browser not launched")
                return False
            
            logger.info(f"Navigating to: {url}")
            
            # Get address bar coordinates
            browser_coords = self.coords.get('browser', {})
            address_bar = browser_coords.get('address_bar', [960, 60])
            
            # Click address bar
            pyautogui.click(address_bar[0], address_bar[1])
            time.sleep(0.3)
            
            # Triple-click to select all
            pyautogui.click(address_bar[0], address_bar[1], clicks=3, interval=0.1)
            time.sleep(0.2)
            
            # Type URL using OSK
            if not self.osk.type_text(url):
                logger.error("Failed to type URL")
                return False
            
            # Press Enter on OSK
            if not self.osk.press_enter():
                logger.error("Failed to press Enter")
                return False
            
            # Wait for page load
            time.sleep(3)
            
            logger.success(f"Navigated to: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to URL: {e}")
            return False
    
    def open_reddit(self) -> bool:
        """
        Open Reddit homepage
        
        Returns:
            True if successful
        """
        return self.navigate_to_url(self.reddit_base)
    
    def search_reddit(self, keyword: str) -> bool:
        """
        Search Reddit for keyword using OSK
        
        Steps:
        1. Click search box
        2. Clear existing text (triple-click + backspace)
        3. Type keyword using OSK
        4. Click Enter on OSK
        
        Args:
            keyword: Search term
        
        Returns:
            True if search successful
        """
        try:
            logger.info(f"Searching Reddit for: '{keyword}'")
            
            # Get search box coordinates
            reddit_coords = self.coords.get('reddit', {})
            search_box = reddit_coords.get('search_box', [800, 80])
            
            # Click search box
            pyautogui.click(search_box[0], search_box[1])
            time.sleep(0.3)
            
            # Clear existing text (triple-click)
            pyautogui.click(search_box[0], search_box[1], clicks=3, interval=0.1)
            time.sleep(0.2)
            
            # Type keyword using OSK
            if not self.osk.type_text(keyword):
                logger.error("Failed to type keyword")
                return False
            
            # Press Enter
            if not self.osk.press_enter():
                logger.error("Failed to submit search")
                return False
            
            # Wait for results to load
            time.sleep(3)
            
            logger.success(f"Search complete for: '{keyword}'")
            return True
            
        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
            return False
    
    def click_tab(self, tab: str) -> bool:
        """
        Click a Reddit tab (Hot/New/Top/Rising) using mouse
        
        Args:
            tab: Tab name ("hot", "new", "top", "rising")
        
        Returns:
            True if click successful
        """
        try:
            reddit_coords = self.coords.get('reddit', {})
            tab_coord_key = f"{tab.lower()}_tab"
            
            tab_coords = reddit_coords.get(tab_coord_key)
            if not tab_coords:
                logger.error(f"Tab coordinates not found for: {tab}")
                return False
            
            # Click tab
            pyautogui.click(tab_coords[0], tab_coords[1])
            time.sleep(2)  # Wait for content to load
            
            logger.info(f"Clicked '{tab}' tab")
            return True
            
        except Exception as e:
            logger.error(f"Error clicking tab '{tab}': {e}")
            return False
    
    def click_post_element(
        self,
        element_name: str,
        element_coords: Tuple[int, int]
    ) -> bool:
        """
        Click an element within a Reddit post (upvote, comment, etc.)
        
        Args:
            element_name: Name of element (for logging)
            element_coords: (x, y) coordinates
        
        Returns:
            True if click successful
        """
        try:
            x, y = element_coords
            pyautogui.click(x, y)
            time.sleep(0.5)
            
            logger.debug(f"Clicked '{element_name}' at ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"Error clicking '{element_name}': {e}")
            return False
    
    def upvote_post(self, upvote_coords: Tuple[int, int]) -> bool:
        """Upvote a Reddit post"""
        return self.click_post_element('upvote', upvote_coords)
    
    def comment_on_post(
        self,
        comment_box_coords: Tuple[int, int],
        comment_text: str
    ) -> bool:
        """
        Comment on a Reddit post using OSK
        
        Args:
            comment_box_coords: (x, y) of comment box
            comment_text: Text to post (max 200 chars)
        
        Returns:
            True if comment posted
        """
        try:
            # Click comment box
            pyautogui.click(comment_box_coords[0], comment_box_coords[1])
            time.sleep(0.5)
            
            # Type comment using OSK
            if not self.osk.type_text(comment_text):
                logger.error("Failed to type comment")
                return False
            
            # Get submit button coordinates
            reddit_coords = self.coords.get('reddit', {})
            submit_coords = reddit_coords.get('comment_submit', [700, 500])
            
            # Click submit
            pyautogui.click(submit_coords[0], submit_coords[1])
            time.sleep(2)
            
            logger.success(f"Comment posted: '{comment_text[:50]}...'")
            return True
            
        except Exception as e:
            logger.error(f"Error posting comment: {e}")
            return False
    
    def scroll_feed(self, max_scrolls: int = 10):
        """
        Scroll through Reddit feed and capture posts
        
        Args:
            max_scrolls: Maximum scrolls
        
        Returns:
            List of captured posts
        """
        try:
            # Reset scroll position
            self.scroller.reset()
            
            # Scroll to top first
            self.scroller.scroll_to_top()
            
            # Capture posts while scrolling
            captured_posts = []
            
            def capture_callback(screenshot, scroll_index):
                # Capture posts from current viewport
                posts = self.screenshot.capture_posts(scroll_position=scroll_index)
                captured_posts.extend(posts)
                return posts
            
            # Scroll and capture
            self.scroller.scroll_and_capture(
                capture_callback=capture_callback,
                max_scrolls=max_scrolls
            )
            
            logger.info(f"Captured {len(captured_posts)} posts total")
            return captured_posts
            
        except Exception as e:
            logger.error(f"Error scrolling feed: {e}")
            return []
    
    def process_keyword(
        self,
        keyword: str,
        tabs: List[str] = ['hot', 'new'],
        max_scrolls_per_tab: int = 5
    ) -> RedditSearchResult:
        """
        Complete workflow: search keyword, process tabs, capture posts
        
        Args:
            keyword: Search term
            tabs: List of tabs to check
            max_scrolls_per_tab: Scrolls per tab
        
        Returns:
            RedditSearchResult summary
        """
        try:
            logger.info(f"Processing keyword: '{keyword}'")
            
            # Search for keyword
            if not self.search_reddit(keyword):
                logger.error(f"Search failed for: {keyword}")
                return None
            
            all_posts = []
            
            # Process each tab
            for tab in tabs:
                logger.info(f"Processing '{tab}' tab...")
                
                # Click tab
                if not self.click_tab(tab):
                    continue
                
                # Scroll and capture
                posts = self.scroll_feed(max_scrolls=max_scrolls_per_tab)
                all_posts.extend(posts)
            
            result = RedditSearchResult(
                keyword=keyword,
                tab=",".join(tabs),
                posts_captured=len(all_posts),
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
            
            logger.success(f"Keyword '{keyword}' complete: {len(all_posts)} posts captured")
            return result
            
        except Exception as e:
            logger.error(f"Error processing keyword '{keyword}': {e}")
            return None
    
    def __enter__(self):
        """Context manager entry"""
        self.launch_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_browser()


if __name__ == "__main__":
    # Test Reddit browser controller
    from loguru import logger
    logger.add("logs/reddit_test.log", rotation="10 MB")
    
    print("=" * 60)
    print("REDDIT BROWSER CONTROLLER TEST")
    print("=" * 60)
    
    # Initialize dependencies
    osk = OSKManager()
    osk.launch_osk()
    osk.calibrate()
    
    scroller = RedditScrollController()
    screenshot = RedditScreenshotEngine(osk_bounds=osk.get_osk_region())
    
    # Create controller
    with RedditBrowserController(osk, scroller, screenshot) as reddit:
        print("✓ Browser launched")
        
        # Test navigation
        print("\nNavigating to Reddit...")
        reddit.open_reddit()
        print("✓ Reddit opened")
        
        # Test search
        print("\nSearching for 'bull put spread'...")
        reddit.search_reddit("bull put spread")
        print("✓ Search complete")
        
        # Test tab clicking
        print("\nClicking 'New' tab...")
        reddit.click_tab("new")
        print("✓ Tab clicked")
        
        print("\n✓ Test complete!")
    
    osk.close_osk()
    print("=" * 60)
