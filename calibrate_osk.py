"""
OSK Calibration Tool
Run this first to calibrate the On-Screen Keyboard.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from osk_manager import OSKManager
from loguru import logger


def main():
    logger.add("logs/calibration.log", rotation="10 MB")
    
    print("=" * 80)
    print("OSK CALIBRATION TOOL")
    print("=" * 80)
    print()
    print("This tool will:")
    print("  1. Launch the Windows On-Screen Keyboard (OSK)")
    print("  2. Auto-detect key positions using OCR")
    print("  3. Save calibration to config/osk_calibration.json")
    print()
    print("Please ensure:")
    print("  - Your screen resolution is 1920x1080")
    print("  - No windows are blocking the bottom of the screen")
    print("  - Tesseract OCR is installed and in PATH")
    print()
    input("Press Enter to begin calibration...")
    print()
    
    try:
        # Create OSK manager
        osk = OSKManager()
        
        # Launch OSK
        print("Launching OSK...")
        if not osk.launch_osk():
            print("❌ Failed to launch OSK")
            return
        
        print("✅ OSK launched")
        print()
        
        # Wait for positioning
        input("Position OSK at the bottom of the screen, then press Enter...")
        print()
        
        # Detect bounds
        print("Detecting OSK window bounds...")
        bounds = osk.detect_osk_bounds()
        if bounds:
            print(f"✅ OSK bounds: {bounds}")
        print()
        
        # Calibrate
        print("Calibrating key positions...")
        print("This may take 30-60 seconds...")
        
        if osk.calibrate(force=True):
            print("✅ Calibration complete!")
            print()
            print(f"Calibration data saved to: {osk.config_path}")
            print()
            
            # Test typing
            print("Testing calibration...")
            print("A test window with a text field should be open.")
            test = input("\nType 'yes' to test typing (or skip): ")
            
            if test.lower() == 'yes':
                print("\nTyping test phrase: 'hello world'")
                print("Watch the active text field...")
                osk.type_text("hello world")
                print("✅ Test complete!")
                print()
                print("If you saw 'hello world' appear, calibration is successful!")
            
        else:
            print("❌ Calibration failed!")
            print("Check logs/calibration.log for details")
        
        # Close OSK
        print("\nClosing OSK...")
        osk.close_osk()
        print("✅ Done!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
