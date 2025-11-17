"""
Test OSK Manager
Unit tests for Virtual On-Screen Keyboard functionality.
"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from osk_manager import OSKManager
from loguru import logger


def test_osk_launch():
    """Test OSK launch and detection"""
    print("\n" + "=" * 60)
    print("TEST: OSK Launch and Detection")
    print("=" * 60)
    
    osk = OSKManager()
    
    # Test launch
    print("Launching OSK...")
    assert osk.launch_osk(), "Failed to launch OSK"
    print("✅ OSK launched")
    
    # Test detection
    print("Checking if OSK is running...")
    assert osk.is_osk_running(), "OSK not detected as running"
    print("✅ OSK detected")
    
    # Test bounds detection
    print("Detecting OSK bounds...")
    bounds = osk.detect_osk_bounds()
    assert bounds is not None, "Failed to detect OSK bounds"
    print(f"✅ OSK bounds: {bounds}")
    
    # Cleanup
    osk.close_osk()
    print("✅ Test passed!")


def test_osk_calibration():
    """Test OSK calibration"""
    print("\n" + "=" * 60)
    print("TEST: OSK Calibration")
    print("=" * 60)
    
    osk = OSKManager()
    osk.launch_osk()
    
    # Test calibration
    print("Running calibration...")
    assert osk.calibrate(force=True), "Calibration failed"
    print("✅ Calibration complete")
    
    # Check calibration data
    print("Checking calibration data...")
    assert len(osk.calibration) > 0, "No calibration data"
    print(f"✅ {len(osk.calibration)} keys calibrated")
    
    # Test key existence
    required_keys = ['a', 'space', 'enter', 'backspace']
    for key in required_keys:
        assert key in osk.calibration, f"Key '{key}' not in calibration"
    print(f"✅ All required keys present")
    
    # Cleanup
    osk.close_osk()
    print("✅ Test passed!")


def test_osk_typing():
    """Test OSK typing (manual verification required)"""
    print("\n" + "=" * 60)
    print("TEST: OSK Typing")
    print("=" * 60)
    print("\nNOTE: This test requires manual verification")
    print("Open Notepad or any text field before proceeding")
    
    input("\nPress Enter when ready...")
    
    osk = OSKManager()
    osk.launch_osk()
    
    if not osk.is_calibrated:
        print("Loading existing calibration...")
        osk.calibrate()
    
    # Give time to focus text field
    print("\nClick into your text field NOW!")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    # Test typing
    test_text = "hello world"
    print(f"\nTyping: '{test_text}'")
    print("Watch your text field...")
    
    success = osk.type_text(test_text)
    
    if success:
        print("\n✅ Typing command executed")
        result = input("\nDid 'hello world' appear in your text field? (y/n): ")
        assert result.lower() == 'y', "Typing verification failed"
        print("✅ Typing verified!")
    else:
        print("❌ Typing failed")
        assert False, "Typing command failed"
    
    # Cleanup
    osk.close_osk()
    print("✅ Test passed!")


def run_all_tests():
    """Run all OSK tests"""
    logger.add("logs/test_osk.log", rotation="10 MB")
    
    print("=" * 60)
    print("OSK MANAGER TEST SUITE")
    print("=" * 60)
    
    try:
        test_osk_launch()
        test_osk_calibration()
        
        # Ask about typing test (requires manual verification)
        response = input("\nRun typing test? (requires manual verification) (y/n): ")
        if response.lower() == 'y':
            test_osk_typing()
        
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
