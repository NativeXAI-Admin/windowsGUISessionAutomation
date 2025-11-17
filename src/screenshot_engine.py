"""
Screenshot Engine - Captures Reddit Posts While Avoiding OSK
Handles all screenshot operations with OSK exclusion.

CRITICAL: Must exclude OSK from captures to avoid interference with LLM analysis.
"""

import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass

import pyautogui
from PIL import Image, ImageDraw
import numpy as np
from loguru import logger


@dataclass
class PostCapture:
    """Captured Reddit post data"""
    image: Image.Image
    position: int  # Scroll position when captured
    timestamp: datetime
    bounds: Tuple[int, int, int, int]  # (left, top, right, bottom)
    clickable_elements: Dict[str, Tuple[int, int]] = None  # Element name -> (x, y)
    
    def save(self, directory: str, prefix: str = "post") -> str:
        """Save capture to file"""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{prefix}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}_{self.position}.png"
        filepath = path / filename
        
        self.image.save(filepath)
        return str(filepath)


class ScreenshotEngine:
    """
    Screenshot Capture Engine
    
    Responsibilities:
    - Capture full viewport screenshots
    - Detect and exclude OSK region from captures
    - Identify individual post boundaries in screenshots
    - Map clickable elements within each post
    - Save screenshots with metadata for LLM analysis
    """
    
    def __init__(
        self,
        output_dir: str = "screenshots",
        osk_bounds: Optional[Tuple[int, int, int, int]] = None
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # OSK exclusion zone
        self.osk_bounds = osk_bounds  # (left, top, right, bottom)
        
        # Screenshot settings
        self.quality = 95
        
        # Post detection settings (for Reddit)
        self.min_post_height = 100
        self.max_post_height = 800
        
        logger.info(f"Screenshot Engine initialized (output: {self.output_dir})")
    
    def set_osk_bounds(self, bounds: Tuple[int, int, int, int]):
        """Set OSK exclusion zone"""
        self.osk_bounds = bounds
        logger.info(f"OSK exclusion zone set: {bounds}")
    
    def capture_full_screen(self) -> Image.Image:
        """
        Capture full screen screenshot
        
        Returns:
            PIL Image
        """
        try:
            screenshot = pyautogui.screenshot()
            logger.debug("Full screen captured")
            return screenshot
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return None
    
    def capture_viewport(self, exclude_osk: bool = True) -> Image.Image:
        """
        Capture viewport (excluding OSK if present)
        
        Args:
            exclude_osk: Whether to exclude OSK region
        
        Returns:
            PIL Image of viewport only
        """
        try:
            # Capture full screen
            full = self.capture_full_screen()
            
            if not exclude_osk or not self.osk_bounds:
                return full
            
            # Crop out OSK region
            left, top, right, bottom = self.osk_bounds
            
            # Get screen size
            width, height = full.size
            
            # Crop to exclude OSK (usually at bottom)
            viewport = full.crop((0, 0, width, top))
            
            logger.debug(f"Viewport captured (excluding OSK)")
            return viewport
            
        except Exception as e:
            logger.error(f"Error capturing viewport: {e}")
            return None
    
    def capture_region(
        self,
        left: int,
        top: int,
        right: int,
        bottom: int
    ) -> Optional[Image.Image]:
        """
        Capture specific screen region
        
        Args:
            left, top, right, bottom: Region coordinates
        
        Returns:
            PIL Image of region
        """
        try:
            # Calculate width and height
            width = right - left
            height = bottom - top
            
            # Capture region
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
            logger.debug(f"Region captured: ({left}, {top}, {right}, {bottom})")
            return screenshot
            
        except Exception as e:
            logger.error(f"Error capturing region: {e}")
            return None
    
    def detect_post_boundaries(
        self,
        screenshot: Image.Image,
        viewport_top: int = 200,
        viewport_bottom: int = 900
    ) -> List[Tuple[int, int, int, int]]:
        """
        Detect individual Reddit post boundaries in screenshot
        
        This is a simplified implementation - in production you'd use
        more sophisticated edge detection or visual markers.
        
        Args:
            screenshot: Screenshot to analyze
            viewport_top: Top of Reddit content area
            viewport_bottom: Bottom of Reddit content area
        
        Returns:
            List of (left, top, right, bottom) tuples for each post
        """
        try:
            # Convert to numpy array
            img_array = np.array(screenshot)
            
            # Simple approach: divide viewport into estimated post regions
            # In production, you'd detect actual post boundaries using:
            # - Edge detection
            # - Color segmentation
            # - Template matching for Reddit UI elements
            
            posts = []
            
            # Estimate 3-5 posts visible at once
            post_height = 250  # Average Reddit post height
            
            current_top = viewport_top
            while current_top < viewport_bottom:
                post_bottom = min(current_top + post_height, viewport_bottom)
                
                # Full width (Reddit posts span viewport width)
                left = 50
                right = screenshot.width - 50
                
                posts.append((left, current_top, right, post_bottom))
                current_top = post_bottom + 10  # Small gap between posts
            
            logger.debug(f"Detected {len(posts)} post regions")
            return posts
            
        except Exception as e:
            logger.error(f"Error detecting post boundaries: {e}")
            return []
    
    def map_post_elements(
        self,
        post_bounds: Tuple[int, int, int, int]
    ) -> Dict[str, Tuple[int, int]]:
        """
        Map clickable elements within a post
        
        Args:
            post_bounds: (left, top, right, bottom) of post
        
        Returns:
            Dict mapping element name to (x, y) coordinates
        """
        left, top, right, bottom = post_bounds
        
        # Estimate element positions relative to post bounds
        # These are approximate - actual positions vary by post type
        elements = {
            'upvote': (left + 30, top + 50),
            'downvote': (left + 30, top + 80),
            'comment': (left + 120, top + bottom - 50),
            'share': (left + 220, top + bottom - 50),
            'save': (left + 320, top + bottom - 50),
        }
        
        return elements
    
    def capture_posts(
        self,
        scroll_position: int = 0
    ) -> List[PostCapture]:
        """
        Capture all visible Reddit posts in current viewport
        
        Args:
            scroll_position: Current scroll position (for metadata)
        
        Returns:
            List of PostCapture objects
        """
        try:
            # Capture viewport (excluding OSK)
            viewport = self.capture_viewport(exclude_osk=True)
            
            if viewport is None:
                return []
            
            # Detect post boundaries
            post_bounds_list = self.detect_post_boundaries(viewport)
            
            # Capture each post
            captures = []
            
            for i, bounds in enumerate(post_bounds_list):
                left, top, right, bottom = bounds
                
                # Crop post from viewport
                post_image = viewport.crop((left, top, right, bottom))
                
                # Map clickable elements
                elements = self.map_post_elements(bounds)
                
                # Create capture object
                capture = PostCapture(
                    image=post_image,
                    position=scroll_position + i,
                    timestamp=datetime.now(),
                    bounds=bounds,
                    clickable_elements=elements
                )
                
                captures.append(capture)
            
            logger.info(f"Captured {len(captures)} posts at scroll position {scroll_position}")
            return captures
            
        except Exception as e:
            logger.error(f"Error capturing posts: {e}")
            return []
    
    def save_screenshot(
        self,
        image: Image.Image,
        prefix: str = "screenshot"
    ) -> str:
        """
        Save screenshot to file
        
        Args:
            image: PIL Image to save
            prefix: Filename prefix
        
        Returns:
            Path to saved file
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.png"
            filepath = self.output_dir / filename
            
            image.save(filepath, quality=self.quality)
            
            logger.debug(f"Screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")
            return ""
    
    def annotate_post(
        self,
        image: Image.Image,
        elements: Dict[str, Tuple[int, int]]
    ) -> Image.Image:
        """
        Annotate post image with clickable element markers
        (Useful for debugging/visualization)
        
        Args:
            image: Post image
            elements: Dict of element name -> (x, y)
        
        Returns:
            Annotated image
        """
        try:
            # Create copy
            annotated = image.copy()
            draw = ImageDraw.Draw(annotated)
            
            # Draw markers for each element
            for name, (x, y) in elements.items():
                # Draw circle
                radius = 10
                draw.ellipse(
                    [(x - radius, y - radius), (x + radius, y + radius)],
                    outline='red',
                    width=2
                )
                
                # Draw label
                draw.text((x + 15, y - 5), name, fill='red')
            
            return annotated
            
        except Exception as e:
            logger.error(f"Error annotating post: {e}")
            return image
    
    def cleanup_old_screenshots(self, days: int = 7):
        """
        Delete screenshots older than N days
        
        Args:
            days: Age threshold in days
        """
        try:
            cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
            deleted = 0
            
            for filepath in self.output_dir.glob("*.png"):
                if filepath.stat().st_mtime < cutoff:
                    filepath.unlink()
                    deleted += 1
            
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} old screenshots")
            
        except Exception as e:
            logger.error(f"Error cleaning up screenshots: {e}")


class RedditScreenshotEngine(ScreenshotEngine):
    """
    Specialized screenshot engine for Reddit
    """
    
    def __init__(
        self,
        output_dir: str = "screenshots/reddit",
        osk_bounds: Optional[Tuple[int, int, int, int]] = None
    ):
        super().__init__(output_dir, osk_bounds)
        
        # Reddit-specific viewport bounds
        self.reddit_viewport_top = 200  # Below header
        self.reddit_viewport_bottom = 900  # Above OSK
        
        logger.info("Reddit Screenshot Engine initialized")
    
    def capture_reddit_feed(self) -> List[PostCapture]:
        """
        Capture current Reddit feed posts
        
        Returns:
            List of PostCapture objects
        """
        return self.capture_posts()
    
    def prepare_for_llm(self, capture: PostCapture) -> Dict:
        """
        Prepare captured post for LLM analysis
        
        Args:
            capture: PostCapture object
        
        Returns:
            Dict with image and metadata for LLM
        """
        try:
            # Save image temporarily
            temp_path = self.save_screenshot(capture.image, prefix="llm_temp")
            
            # Build metadata
            metadata = {
                'image_path': temp_path,
                'timestamp': capture.timestamp.isoformat(),
                'position': capture.position,
                'bounds': capture.bounds,
                'clickable_elements': capture.clickable_elements
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error preparing for LLM: {e}")
            return {}


if __name__ == "__main__":
    # Test screenshot engine
    from loguru import logger
    logger.add("logs/screenshot_test.log", rotation="10 MB")
    
    print("=" * 60)
    print("SCREENSHOT ENGINE TEST")
    print("=" * 60)
    
    # Create engine
    engine = ScreenshotEngine()
    
    # Test full screen capture
    print("\nCapturing full screen...")
    full = engine.capture_full_screen()
    if full:
        print(f"✓ Full screen: {full.size}")
    
    # Test viewport capture (with mock OSK bounds)
    print("\nTesting viewport capture (excluding OSK)...")
    engine.set_osk_bounds((0, 800, 1000, 1080))
    viewport = engine.capture_viewport(exclude_osk=True)
    if viewport:
        print(f"✓ Viewport: {viewport.size}")
    
    # Test saving
    print("\nTesting save...")
    if viewport:
        path = engine.save_screenshot(viewport, prefix="test")
        print(f"✓ Saved: {path}")
    
    print("\n✓ Test complete!")
    print("=" * 60)
