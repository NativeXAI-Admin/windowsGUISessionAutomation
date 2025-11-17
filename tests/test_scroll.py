"""
Test Scroll Controller
Unit tests for mouse wheel scrolling functionality.
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scroll_controller import ScrollController, RedditScrollController
from loguru import logger


def test_scroll_initialization():
    """Test scroll controller initialization"""
    print("\n" + "=" * 60)
    print("TEST: Scroll Controller Initialization")
    print("=" * 60)
    
    controller = ScrollController()
    
    assert controller.config is not None, "Config not loaded"
    assert controller.step_size > 0, "Invalid step size"
    assert controller.max_scrolls > 0, "Invalid max scrolls"
    
    print(f"✅ Config loaded")
    print(f"   Step size: {controller.step_size}px")
    print(f"   Max scrolls: {controller.max_scrolls}")
    print("✅ Test passed!")


def test_scroll_down():
    """Test scrolling down"""
    print("\n" + "=" * 60)
    print("TEST: Scroll Down")
    print("=" * 60)
    print("\nNOTE: Open a browser window before proceeding")
    
    input("\nPress Enter when ready...")
    
    controller = ScrollController()
    
    print("\nScrolling down in 3 seconds...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # Test scroll down
    success = controller.scroll_down()
    assert success, "Scroll down failed"
    print("✅ Scrolled down")
    
    assert controller.position.scroll_count == 1, "Scroll count not updated"
    print(f"✅ Scroll count: {controller.position.scroll_count}")
    
    print("✅ Test passed!")


def test_scroll_to_top():
    """Test scrolling to top"""
    print("\n" + "=" * 60)
    print("TEST: Scroll to Top")
    print("=" * 60)
    print("\nNOTE: Make sure browser window has scrolled content")
    
    input("\nPress Enter when ready...")
    
    controller = ScrollController()
    
    # Scroll down first
    print("\nScrolling down a few times...")
    for _ in range(3):
        controller.scroll_down()
        time.sleep(0.5)
    
    print(f"Current scroll count: {controller.position.scroll_count}")
    
    # Scroll to top
    print("\nScrolling to top...")
    success = controller.scroll_to_top()
    assert success, "Scroll to top failed"
    print("✅ Scrolled to top")
    
    assert controller.position.scroll_count == 0, "Position not reset"
    print("✅ Position reset")
    
    print("✅ Test passed!")


def test_reddit_scroll_controller():
    """Test Reddit-specific scroll controller"""
    print("\n" + "=" * 60)
    print("TEST: Reddit Scroll Controller")
    print("=" * 60)
    
    controller = RedditScrollController()
    
    assert controller.posts_per_scroll > 0, "Invalid posts per scroll"
    assert controller.max_posts > 0, "Invalid max posts"
    
    print(f"✅ Reddit config loaded")
    print(f"   Posts per scroll: {controller.posts_per_scroll}")
    print(f"   Max posts: {controller.max_posts}")
    print("✅ Test passed!")


def run_all_tests():
    """Run all scroll tests"""
    logger.add("logs/test_scroll.log", rotation="10 MB")
    
    print("=" * 60)
    print("SCROLL CONTROLLER TEST SUITE")
    print("=" * 60)
    
    try:
        test_scroll_initialization()
        test_reddit_scroll_controller()
        
        # Ask about interactive tests
        response = input("\nRun interactive scroll tests? (requires open browser) (y/n): ")
        if response.lower() == 'y':
            test_scroll_down()
            test_scroll_to_top()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
