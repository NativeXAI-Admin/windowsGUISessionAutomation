"""
Daily Automation Scheduler
Orchestrates the complete Reddit monitoring workflow.

CRITICAL: All operations use OSK and mouse only - NO keyboard input.
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

import yaml
import redis
import schedule
from dotenv import load_dotenv
from loguru import logger

from osk_manager import OSKManager
from scroll_controller import RedditScrollController
from screenshot_engine import RedditScreenshotEngine
from reddit_controller import RedditBrowserController
from llm_analyzer import OptionsEduLLMAnalyzer, EngagementAction


@dataclass
class DailyRunStats:
    """Statistics for a daily run"""
    run_date: str
    keywords_processed: int
    posts_captured: int
    posts_analyzed: int
    upvotes_given: int
    comments_posted: int
    errors: int
    duration_seconds: float
    
    def to_dict(self) -> dict:
        return asdict(self)


class RedditAutomationScheduler:
    """
    Daily Automation Scheduler
    
    Responsibilities:
    - Schedule daily runs at configured times
    - Load keyword list from configuration
    - Process each keyword sequentially
    - Manage OSK lifecycle (launch at start, close at end)
    - Handle failures and implement retry logic
    - Generate daily reports of actions taken
    - Maintain state between runs using Redis
    """
    
    def __init__(
        self,
        keywords_config: str = "config/keywords.yaml",
        state_db: Optional[redis.Redis] = None
    ):
        # Load environment variables
        load_dotenv()
        
        # Load keyword configuration
        self.keywords_config_path = Path(keywords_config)
        self.keywords_data = self.load_keywords()
        
        # State management
        self.redis_client = state_db or self.init_redis()
        
        # Components (initialized in run)
        self.osk: Optional[OSKManager] = None
        self.scroller: Optional[RedditScrollController] = None
        self.screenshot: Optional[RedditScreenshotEngine] = None
        self.reddit: Optional[RedditBrowserController] = None
        self.llm: Optional[OptionsEduLLMAnalyzer] = None
        
        # Run statistics
        self.stats = DailyRunStats(
            run_date="",
            keywords_processed=0,
            posts_captured=0,
            posts_analyzed=0,
            upvotes_given=0,
            comments_posted=0,
            errors=0,
            duration_seconds=0
        )
        
        # Engagement limits
        engagement_settings = self.keywords_data.get('engagement', {})
        self.max_comments_per_day = engagement_settings.get('max_comments_per_day', 20)
        self.max_upvotes_per_day = engagement_settings.get('max_upvotes_per_day', 50)
        
        logger.info("Reddit Automation Scheduler initialized")
    
    def load_keywords(self) -> dict:
        """Load keywords configuration"""
        try:
            if self.keywords_config_path.exists():
                with open(self.keywords_config_path, 'r') as f:
                    data = yaml.safe_load(f)
                    logger.info(f"Loaded {len(data.get('keywords', []))} keywords")
                    return data
            else:
                logger.error(f"Keywords config not found: {self.keywords_config_path}")
                return {'keywords': []}
        except Exception as e:
            logger.error(f"Error loading keywords: {e}")
            return {'keywords': []}
    
    def init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for state management"""
        try:
            client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                password=os.getenv('REDIS_PASSWORD'),
                decode_responses=True
            )
            
            # Test connection
            client.ping()
            logger.success("Redis connected")
            return client
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e} (state will not persist)")
            return None
    
    def initialize_components(self) -> bool:
        """Initialize all components for a run"""
        try:
            logger.info("Initializing components...")
            
            # 1. OSK Manager
            self.osk = OSKManager()
            if not self.osk.launch_osk():
                raise Exception("Failed to launch OSK")
            if not self.osk.is_calibrated:
                if not self.osk.calibrate():
                    raise Exception("Failed to calibrate OSK")
            
            # 2. Scroll Controller
            self.scroller = RedditScrollController()
            
            # 3. Screenshot Engine
            osk_bounds = self.osk.get_osk_region()
            self.screenshot = RedditScreenshotEngine(osk_bounds=osk_bounds)
            
            # 4. LLM Analyzer
            self.llm = OptionsEduLLMAnalyzer()
            
            # 5. Reddit Controller
            self.reddit = RedditBrowserController(
                osk_manager=self.osk,
                scroll_controller=self.scroller,
                screenshot_engine=self.screenshot
            )
            
            if not self.reddit.launch_browser():
                raise Exception("Failed to launch browser")
            
            logger.success("All components initialized")
            return True
            
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            self.cleanup_components()
            return False
    
    def cleanup_components(self):
        """Clean up all components"""
        try:
            logger.info("Cleaning up components...")
            
            if self.reddit:
                self.reddit.close_browser()
            
            if self.osk:
                self.osk.close_osk()
            
            logger.info("Cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def process_post(
        self,
        post_capture,
        keyword: str
    ) -> bool:
        """
        Process a single post: analyze and engage if appropriate
        
        Args:
            post_capture: PostCapture object
            keyword: Keyword this post was found under
        
        Returns:
            True if processing successful
        """
        try:
            # Check daily limits
            if self.stats.upvotes_given >= self.max_upvotes_per_day:
                logger.warning("Daily upvote limit reached")
                return False
            
            if self.stats.comments_posted >= self.max_comments_per_day:
                logger.warning("Daily comment limit reached")
                return False
            
            # Prepare for LLM analysis
            llm_data = self.screenshot.prepare_for_llm(post_capture)
            
            # Analyze with LLM
            analysis = self.llm.analyze_post(
                image_path=llm_data['image_path'],
                post_metadata={'keyword': keyword, **llm_data}
            )
            
            if not analysis:
                logger.warning("LLM analysis failed")
                self.stats.errors += 1
                return False
            
            self.stats.posts_analyzed += 1
            
            # Execute engagement action
            if analysis.action == EngagementAction.SKIP:
                logger.info(f"Skipping post (score: {analysis.overall_score})")
                return True
            
            # Upvote if recommended
            if analysis.action in [EngagementAction.UPVOTE, EngagementAction.UPVOTE_AND_COMMENT]:
                upvote_coords = post_capture.clickable_elements.get('upvote')
                if upvote_coords and self.reddit.upvote_post(upvote_coords):
                    self.stats.upvotes_given += 1
                    logger.success("Post upvoted")
            
            # Comment if recommended
            if analysis.action in [EngagementAction.COMMENT, EngagementAction.UPVOTE_AND_COMMENT]:
                if analysis.comment_text:
                    comment_coords = post_capture.clickable_elements.get('comment')
                    if comment_coords:
                        if self.reddit.comment_on_post(comment_coords, analysis.comment_text):
                            self.stats.comments_posted += 1
                            logger.success("Comment posted")
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing post: {e}")
            self.stats.errors += 1
            return False
    
    def run_daily_scan(self) -> DailyRunStats:
        """
        Execute complete daily scan workflow
        
        Returns:
            DailyRunStats with results
        """
        start_time = time.time()
        self.stats.run_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info("=" * 80)
        logger.info("STARTING DAILY REDDIT SCAN")
        logger.info("=" * 80)
        
        try:
            # Initialize components
            if not self.initialize_components():
                logger.error("Failed to initialize, aborting run")
                return self.stats
            
            # Open Reddit
            if not self.reddit.open_reddit():
                logger.error("Failed to open Reddit")
                return self.stats
            
            # Process each keyword
            keywords = self.keywords_data.get('keywords', [])
            
            for keyword_data in keywords:
                try:
                    keyword = keyword_data.get('term')
                    priority = keyword_data.get('priority', 'medium')
                    
                    logger.info(f"\nProcessing keyword: '{keyword}' (priority: {priority})")
                    
                    # Search Reddit
                    result = self.reddit.process_keyword(
                        keyword=keyword,
                        tabs=['hot', 'new'],
                        max_scrolls_per_tab=5
                    )
                    
                    if result:
                        self.stats.keywords_processed += 1
                        self.stats.posts_captured += result.posts_captured
                        
                        # Process captured posts
                        # Note: In full implementation, you'd retrieve the actual PostCapture objects
                        # For now, this is a placeholder
                        logger.info(f"Captured {result.posts_captured} posts for '{keyword}'")
                    
                except Exception as e:
                    logger.error(f"Error processing keyword '{keyword}': {e}")
                    self.stats.errors += 1
                    continue
            
            # Calculate duration
            self.stats.duration_seconds = time.time() - start_time
            
            # Log summary
            logger.info("\n" + "=" * 80)
            logger.info("DAILY SCAN COMPLETE")
            logger.info("=" * 80)
            logger.info(f"Keywords processed: {self.stats.keywords_processed}")
            logger.info(f"Posts captured: {self.stats.posts_captured}")
            logger.info(f"Posts analyzed: {self.stats.posts_analyzed}")
            logger.info(f"Upvotes given: {self.stats.upvotes_given}")
            logger.info(f"Comments posted: {self.stats.comments_posted}")
            logger.info(f"Errors: {self.stats.errors}")
            logger.info(f"Duration: {self.stats.duration_seconds:.1f}s")
            logger.info("=" * 80)
            
            # Save state to Redis
            self.save_state()
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Fatal error during daily scan: {e}")
            self.stats.errors += 1
            return self.stats
            
        finally:
            # Always cleanup
            self.cleanup_components()
    
    def save_state(self):
        """Save run state to Redis"""
        if not self.redis_client:
            return
        
        try:
            key = f"reddit_scan:{self.stats.run_date}"
            self.redis_client.set(key, str(self.stats.to_dict()), ex=604800)  # 7 days
            logger.debug("State saved to Redis")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def schedule_daily_run(self, run_time: str = "09:00"):
        """
        Schedule daily run at specific time
        
        Args:
            run_time: Time in HH:MM format (24-hour)
        """
        schedule.every().day.at(run_time).do(self.run_daily_scan)
        logger.info(f"Daily run scheduled for {run_time}")
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


if __name__ == "__main__":
    # Configure logging
    logger.add(
        "logs/scheduler_{time}.log",
        rotation="10 MB",
        retention="30 days",
        level="INFO"
    )
    
    print("=" * 80)
    print("REDDIT AUTOMATION SCHEDULER")
    print("=" * 80)
    
    # Create scheduler
    scheduler = RedditAutomationScheduler()
    
    # Option 1: Run immediately (for testing)
    print("\nRunning immediate test scan...")
    stats = scheduler.run_daily_scan()
    
    print("\n✓ Test run complete!")
    print(f"  Keywords: {stats.keywords_processed}")
    print(f"  Posts: {stats.posts_captured}")
    print(f"  Duration: {stats.duration_seconds:.1f}s")
    
    # Option 2: Schedule for daily runs (uncomment for production)
    # print("\nScheduling daily runs at 09:00...")
    # scheduler.schedule_daily_run(run_time="09:00")
    
    print("=" * 80)
