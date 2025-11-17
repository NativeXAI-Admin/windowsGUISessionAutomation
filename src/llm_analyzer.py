"""
LLM Analyzer - Options Edu Integration
Analyzes Reddit posts and decides engagement strategy using Claude AI.

CRITICAL: Generates OSK-compatible text (no special unicode characters).
"""

import os
import time
import json
import base64
from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import yaml
from anthropic import Anthropic
from PIL import Image
from loguru import logger


class EngagementAction(Enum):
    """Possible engagement actions"""
    SKIP = "skip"
    UPVOTE = "upvote"
    COMMENT = "comment"
    UPVOTE_AND_COMMENT = "upvote_and_comment"


@dataclass
class LLMAnalysisResult:
    """Result from LLM analysis of a Reddit post"""
    overall_score: float  # 0-100
    relevance: float  # 0-100
    quality: float  # 0-100
    educational_value: float  # 0-100
    engagement_potential: float  # 0-100
    action: EngagementAction
    comment_text: Optional[str] = None
    reasoning: str = ""


class OptionsEduLLMAnalyzer:
    """
    Options Edu LLM Integration
    
    Responsibilities:
    - Send screenshot images to Claude API
    - Receive structured decisions about engagement
    - Generate appropriate response text for comments
    - Ensure generated text is OSK-typeable
    - Handle API rate limiting and retries
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        config_path: str = "config/llm_config.yaml"
    ):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        
        # API settings
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")
        
        # Initialize Claude client
        self.client = Anthropic(api_key=self.api_key)
        
        # Model settings
        api_config = self.config.get('api', {})
        self.model = api_config.get('model', 'claude-sonnet-4-5-20250929')
        self.max_tokens = api_config.get('max_tokens', 1024)
        self.temperature = api_config.get('temperature', 0.3)
        
        # Analysis thresholds
        thresholds = self.config.get('analysis', {}).get('thresholds', {})
        self.min_upvote_confidence = thresholds.get('min_confidence_to_upvote', 70)
        self.min_comment_confidence = thresholds.get('min_confidence_to_comment', 80)
        
        # Rate limiting
        rate_limits = self.config.get('rate_limits', {})
        self.requests_per_minute = rate_limits.get('requests_per_minute', 20)
        self.last_request_time = 0
        self.request_count = 0
        
        logger.info("Options Edu LLM Analyzer initialized")
    
    def load_config(self) -> dict:
        """Load LLM configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    logger.info("LLM config loaded")
                    return config
            else:
                logger.warning(f"Config not found: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading LLM config: {e}")
            return {}
    
    def encode_image(self, image_path: str) -> str:
        """
        Encode image to base64 for Claude API
        
        Args:
            image_path: Path to image file
        
        Returns:
            Base64 encoded string
        """
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                encoded = base64.b64encode(image_data).decode('utf-8')
                return encoded
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            return ""
    
    def rate_limit_check(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # If less than 60 seconds, check request count
        if time_since_last < 60:
            if self.request_count >= self.requests_per_minute:
                sleep_time = 60 - time_since_last
                logger.warning(f"Rate limit reached, sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
                self.request_count = 0
        else:
            # Reset counter after 60 seconds
            self.request_count = 0
        
        self.last_request_time = current_time
        self.request_count += 1
    
    def analyze_post(
        self,
        image_path: str,
        post_metadata: Optional[Dict] = None
    ) -> Optional[LLMAnalysisResult]:
        """
        Analyze Reddit post screenshot using Claude
        
        Args:
            image_path: Path to post screenshot
            post_metadata: Additional context about post
        
        Returns:
            LLMAnalysisResult or None if analysis fails
        """
        try:
            logger.info(f"Analyzing post: {image_path}")
            
            # Rate limit check
            self.rate_limit_check()
            
            # Encode image
            image_base64 = self.encode_image(image_path)
            if not image_base64:
                return None
            
            # Build prompt
            prompt = self._build_analysis_prompt(post_metadata)
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            # Parse response
            content = response.content[0].text
            result = self._parse_analysis_response(content)
            
            logger.success(f"Post analyzed: {result.action.value} (score: {result.overall_score})")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing post: {e}")
            return None
    
    def _build_analysis_prompt(self, post_metadata: Optional[Dict] = None) -> str:
        """Build analysis prompt for Claude"""
        
        prompt_template = self.config.get('prompts', {}).get('post_analysis', "")
        
        if not prompt_template:
            prompt_template = """
You are an expert options trader analyzing a Reddit post.

Evaluate this post for:
1. Relevance to options trading (0-100)
2. Quality and accuracy (0-100)
3. Educational value (0-100)
4. Community engagement potential (0-100)

Provide your analysis in JSON format:
{
  "overall_score": <0-100>,
  "relevance": <0-100>,
  "quality": <0-100>,
  "educational_value": <0-100>,
  "engagement_potential": <0-100>,
  "action": "upvote" | "comment" | "skip",
  "comment_text": "<200 chars or null>",
  "reasoning": "<brief explanation>"
}

IMPORTANT: If you generate comment_text, keep it under 200 characters and use only standard ASCII characters (no emojis or special unicode).
"""
        
        # Add metadata context if provided
        if post_metadata:
            prompt_template += f"\n\nPost Context: {json.dumps(post_metadata, indent=2)}"
        
        return prompt_template
    
    def _parse_analysis_response(self, response_text: str) -> LLMAnalysisResult:
        """
        Parse Claude's JSON response into LLMAnalysisResult
        
        Args:
            response_text: Raw response from Claude
        
        Returns:
            LLMAnalysisResult object
        """
        try:
            # Extract JSON from response
            # Handle markdown code blocks if present
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                json_str = response_text[start:end].strip()
            else:
                json_str = response_text.strip()
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Map action string to enum
            action_str = data.get('action', 'skip').lower()
            action = EngagementAction.SKIP
            
            if action_str == 'upvote':
                action = EngagementAction.UPVOTE
            elif action_str == 'comment':
                action = EngagementAction.COMMENT
            elif 'upvote' in action_str and 'comment' in action_str:
                action = EngagementAction.UPVOTE_AND_COMMENT
            
            # Create result
            result = LLMAnalysisResult(
                overall_score=float(data.get('overall_score', 0)),
                relevance=float(data.get('relevance', 0)),
                quality=float(data.get('quality', 0)),
                educational_value=float(data.get('educational_value', 0)),
                engagement_potential=float(data.get('engagement_potential', 0)),
                action=action,
                comment_text=data.get('comment_text'),
                reasoning=data.get('reasoning', '')
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            # Return default "skip" result
            return LLMAnalysisResult(
                overall_score=0,
                relevance=0,
                quality=0,
                educational_value=0,
                engagement_potential=0,
                action=EngagementAction.SKIP,
                reasoning=f"Parse error: {str(e)}"
            )
    
    def generate_comment(
        self,
        post_summary: str,
        max_length: int = 200
    ) -> Optional[str]:
        """
        Generate OSK-typeable comment text
        
        Args:
            post_summary: Brief summary of post content
            max_length: Maximum comment length
        
        Returns:
            Comment text or None
        """
        try:
            logger.info("Generating comment...")
            
            # Rate limit check
            self.rate_limit_check()
            
            # Build prompt
            prompt_template = self.config.get('prompts', {}).get('comment_generation', "")
            prompt = prompt_template.format(post_summary=post_summary)
            
            # Call Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract comment text
            comment = response.content[0].text.strip()
            
            # Truncate if needed
            if len(comment) > max_length:
                comment = comment[:max_length-3] + "..."
            
            # Validate OSK-typeable (basic ASCII check)
            comment = self._ensure_osk_typeable(comment)
            
            logger.success(f"Generated comment: '{comment}'")
            return comment
            
        except Exception as e:
            logger.error(f"Error generating comment: {e}")
            return None
    
    def _ensure_osk_typeable(self, text: str) -> str:
        """
        Ensure text contains only OSK-typeable characters
        
        Args:
            text: Original text
        
        Returns:
            Cleaned text with only basic ASCII
        """
        # Define allowed characters (what OSK can type)
        allowed = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?-\'"')
        
        # Filter text
        cleaned = ''.join(char if char in allowed else ' ' for char in text)
        
        # Remove multiple spaces
        cleaned = ' '.join(cleaned.split())
        
        return cleaned


if __name__ == "__main__":
    # Test LLM analyzer
    from loguru import logger
    logger.add("logs/llm_test.log", rotation="10 MB")
    
    print("=" * 60)
    print("LLM ANALYZER TEST")
    print("=" * 60)
    
    # Initialize analyzer
    try:
        analyzer = OptionsEduLLMAnalyzer()
        print("✓ Analyzer initialized")
        
        # Test comment generation
        print("\nGenerating test comment...")
        comment = analyzer.generate_comment(
            "Discussion about bull put spreads on SPY"
        )
        if comment:
            print(f"✓ Comment: '{comment}'")
        
        # Test OSK validation
        print("\nTesting OSK validation...")
        test_text = "Hello! This has émojis 😊 and unicode ∑"
        cleaned = analyzer._ensure_osk_typeable(test_text)
        print(f"Original: {test_text}")
        print(f"Cleaned:  {cleaned}")
        print("✓ OSK validation works")
        
        print("\n✓ Test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("=" * 60)
