"""
Manual Reddit Test
Test the complete Reddit workflow manually.
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from osk_manager import OSKManager
from scroll_controller import RedditScrollController
from screenshot_engine import RedditScreenshotEngine
from reddit_controller import RedditBrowserController
from loguru import logger


def main():
    logger.add("logs/manual_test.log", rotation="10 MB")
    
    print("=" * 80)
    print("MANUAL REDDIT TEST")
    print("=" * 80)
    print()
    print("This test will:")
    print("  1. Launch OSK and browser")
    print("  2. Navigate to Reddit")
    print("  3. Search for 'bull put spread'")
    print("  4. Click through Hot/New tabs")
    print("  5. Scroll and capture screenshots")
    print()
    input("Press Enter to begin test...")
    print()
    
    osk = None
    
    try:
        # Initialize OSK
        print("Launching OSK...")
        osk = OSKManager()
        osk.launch_osk()
        
        if not osk.is_calibrated:
            print("⚠️  OSK not calibrated!")
            print("Please run: python calibrate_osk.py")
            return
        
        print("✅ OSK ready")
        
        # Initialize components
        print("Initializing components...")
        scroller = RedditScrollController()
        screenshot = RedditScreenshotEngine(osk_bounds=osk.get_osk_region())
        
        reddit = RedditBrowserController(
            osk_manager=osk,
            scroll_controller=scroller,
            screenshot_engine=screenshot
        )
        
        print("✅ Components initialized")
        
        # Launch browser
        print("\nLaunching browser...")
        reddit.launch_browser()
        time.sleep(2)
        print("✅ Browser launched")
        
        # Navigate to Reddit
        print("\nNavigating to Reddit...")
        reddit.open_reddit()
        time.sleep(3)
        print("✅ Reddit opened")
        
        # Search
        print("\nSearching for 'bull put spread'...")
        reddit.search_reddit("bull put spread")
        time.sleep(3)
        print("✅ Search complete")
        
        # Click Hot tab
        print("\nClicking 'Hot' tab...")
        reddit.click_tab("hot")
        time.sleep(2)
        print("✅ Hot tab selected")
        
        # Scroll and capture
        print("\nScrolling and capturing posts...")
        posts = reddit.scroll_feed(max_scrolls=3)
        print(f"✅ Captured {len(posts)} posts")
        
        # Click New tab
        print("\nClicking 'New' tab...")
        reddit.click_tab("new")
        time.sleep(2)
        print("✅ New tab selected")
        
        # Scroll and capture again
        print("\nScrolling and capturing posts...")
        posts = reddit.scroll_feed(max_scrolls=3)
        print(f"✅ Captured {len(posts)} posts")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETE!")
        print("=" * 80)
        print()
        print("Check screenshots/ directory for captured images")
        
        # Keep browser open for inspection
        input("\nPress Enter to close browser and exit...")
        
        # Cleanup
        reddit.close_browser()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if osk:
            osk.close_osk()
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
