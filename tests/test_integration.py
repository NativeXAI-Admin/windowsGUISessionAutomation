"""
Integration Test - Complete Workflow
Tests the full Reddit automation workflow end-to-end.
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from osk_manager import OSKManager
from scroll_controller import RedditScrollController
from screenshot_engine import RedditScreenshotEngine
from reddit_controller import RedditBrowserController
from llm_analyzer import OptionsEduLLMAnalyzer
from loguru import logger


def test_complete_workflow():
    """Test complete Reddit automation workflow"""
    
    print("=" * 80)
    print("INTEGRATION TEST - COMPLETE WORKFLOW")
    print("=" * 80)
    print()
    print("This test will:")
    print("  1. ✅ Initialize all components")
    print("  2. ✅ Launch OSK and browser")
    print("  3. ✅ Navigate to Reddit")
    print("  4. ✅ Search for keyword")
    print("  5. ✅ Scroll and capture posts")
    print("  6. ✅ Analyze with LLM (if configured)")
    print("  7. ✅ Clean up")
    print()
    input("Press Enter to begin...")
    print()
    
    osk = None
    reddit = None
    
    try:
        # Step 1: Initialize components
        print("STEP 1: Initializing components...")
        print("-" * 60)
        
        osk = OSKManager()
        assert osk.launch_osk(), "Failed to launch OSK"
        print("✅ OSK launched")
        
        if not osk.is_calibrated:
            print("⚠️  OSK not calibrated, calibrating now...")
            assert osk.calibrate(), "Calibration failed"
        print("✅ OSK calibrated")
        
        scroller = RedditScrollController()
        print("✅ Scroll controller ready")
        
        screenshot = RedditScreenshotEngine(osk_bounds=osk.get_osk_region())
        print("✅ Screenshot engine ready")
        
        # LLM (optional - requires API key)
        llm = None
        try:
            llm = OptionsEduLLMAnalyzer()
            print("✅ LLM analyzer ready")
        except Exception as e:
            print(f"⚠️  LLM not available: {e}")
        
        reddit = RedditBrowserController(
            osk_manager=osk,
            scroll_controller=scroller,
            screenshot_engine=screenshot
        )
        print("✅ Reddit controller ready")
        
        # Step 2: Launch browser
        print("\nSTEP 2: Launching browser...")
        print("-" * 60)
        assert reddit.launch_browser(), "Failed to launch browser"
        time.sleep(2)
        print("✅ Browser launched")
        
        # Step 3: Navigate to Reddit
        print("\nSTEP 3: Navigating to Reddit...")
        print("-" * 60)
        assert reddit.open_reddit(), "Failed to open Reddit"
        time.sleep(3)
        print("✅ Reddit opened")
        
        # Step 4: Search
        print("\nSTEP 4: Searching for keyword...")
        print("-" * 60)
        test_keyword = "bull put spread"
        print(f"Keyword: '{test_keyword}'")
        assert reddit.search_reddit(test_keyword), "Search failed"
        time.sleep(3)
        print("✅ Search complete")
        
        # Step 5: Scroll and capture
        print("\nSTEP 5: Scrolling and capturing posts...")
        print("-" * 60)
        posts = reddit.scroll_feed(max_scrolls=2)
        print(f"✅ Captured {len(posts)} posts")
        
        # Step 6: LLM Analysis (if available)
        if llm and len(posts) > 0:
            print("\nSTEP 6: LLM Analysis...")
            print("-" * 60)
            
            # Analyze first post
            first_post = posts[0]
            llm_data = screenshot.prepare_for_llm(first_post)
            
            print(f"Analyzing post at {llm_data['image_path']}...")
            analysis = llm.analyze_post(
                image_path=llm_data['image_path'],
                post_metadata={'keyword': test_keyword}
            )
            
            if analysis:
                print(f"✅ LLM Analysis complete")
                print(f"   Score: {analysis.overall_score}")
                print(f"   Action: {analysis.action.value}")
                print(f"   Reasoning: {analysis.reasoning[:100]}...")
            else:
                print("⚠️  LLM analysis returned None")
        else:
            print("\nSTEP 6: LLM Analysis (skipped)")
            print("-" * 60)
            print("⚠️  LLM not available or no posts captured")
        
        # Step 7: Cleanup
        print("\nSTEP 7: Cleanup...")
        print("-" * 60)
        reddit.close_browser()
        print("✅ Browser closed")
        
        osk.close_osk()
        print("✅ OSK closed")
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ INTEGRATION TEST PASSED!")
        print("=" * 80)
        print(f"\nSummary:")
        print(f"  • Posts captured: {len(posts)}")
        if llm and analysis:
            print(f"  • LLM analysis: Success")
        print(f"  • Screenshots saved to: {screenshot.output_dir}")
        print("=" * 80)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Ensure cleanup
        if reddit:
            try:
                reddit.close_browser()
            except:
                pass
        
        if osk:
            try:
                osk.close_osk()
            except:
                pass


if __name__ == "__main__":
    logger.add("logs/test_integration.log", rotation="10 MB")
    
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
