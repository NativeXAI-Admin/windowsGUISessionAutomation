"""
Main Entry Point - Reddit Automation System
Complete workflow orchestration.

Run this file to start the Reddit automation system.
"""

import sys
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from scheduler import RedditAutomationScheduler


def setup_logging():
    """Configure logging for the application"""
    logger.remove()  # Remove default handler
    
    # Console output
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    # File output
    logger.add(
        "logs/reddit_automation_{time}.log",
        rotation="10 MB",
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    logger.success("Logging configured")


def main():
    """Main entry point"""
    
    print("=" * 80)
    print(" " * 20 + "REDDIT AUTOMATION SYSTEM")
    print(" " * 15 + "Windows Server - Zero Keyboard Access")
    print("=" * 80)
    print()
    
    # Setup logging
    setup_logging()
    
    logger.info("Starting Reddit Automation System...")
    logger.info("Environment: Windows Server")
    logger.info("Input Methods: Mouse + Virtual On-Screen Keyboard ONLY")
    logger.info("Keyboard Access: DISABLED")
    
    try:
        # Create scheduler
        scheduler = RedditAutomationScheduler()
        
        # Option 1: Run immediately (for testing)
        logger.info("\n🚀 Running immediate scan (test mode)...")
        stats = scheduler.run_daily_scan()
        
        # Display results
        print()
        print("=" * 80)
        print("SCAN RESULTS")
        print("=" * 80)
        print(f"📅 Date: {stats.run_date}")
        print(f"🔑 Keywords Processed: {stats.keywords_processed}")
        print(f"📸 Posts Captured: {stats.posts_captured}")
        print(f"🔍 Posts Analyzed: {stats.posts_analyzed}")
        print(f"👍 Upvotes Given: {stats.upvotes_given}")
        print(f"💬 Comments Posted: {stats.comments_posted}")
        print(f"❌ Errors: {stats.errors}")
        print(f"⏱️  Duration: {stats.duration_seconds:.1f} seconds")
        print("=" * 80)
        
        # Option 2: Schedule for daily runs (uncomment for production)
        # logger.info("\n📅 Scheduling daily runs at 09:00...")
        # scheduler.schedule_daily_run(run_time="09:00")
        
        logger.success("Automation complete!")
        
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Interrupted by user")
        print("\nShutting down gracefully...")
        
    except Exception as e:
        logger.error(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("=" * 80)
    print("Thank you for using Reddit Automation System!")
    print("=" * 80)


if __name__ == "__main__":
    main()
