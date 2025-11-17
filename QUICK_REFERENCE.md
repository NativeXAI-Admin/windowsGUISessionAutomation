# Quick Reference - Reddit Automation System

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup environment
copy .env.example .env
# Edit .env with your Anthropic API key

# 3. Calibrate OSK (CRITICAL FIRST STEP)
python calibrate_osk.py

# 4. Test the system
python manual_reddit_test.py

# 5. Run automation
python main.py
```

---

## 📁 Project Structure

```
windowsGUISessionAutomation/
├── src/
│   ├── osk_manager.py           # Virtual keyboard control
│   ├── scroll_controller.py     # Mouse wheel scrolling
│   ├── screenshot_engine.py     # Capture posts (exclude OSK)
│   ├── reddit_controller.py     # Browser automation
│   ├── llm_analyzer.py          # Claude AI analysis
│   └── scheduler.py             # Daily automation
├── config/
│   ├── keywords.yaml            # Search terms
│   ├── osk_calibration.json     # Key coordinates
│   ├── screen_coordinates.json  # Reddit UI positions
│   ├── llm_config.yaml          # AI settings
│   └── scroll_settings.json     # Scroll parameters
├── tests/
│   ├── test_osk.py              # OSK tests
│   ├── test_scroll.py           # Scroll tests
│   └── test_integration.py      # End-to-end test
├── logs/                        # Application logs
├── screenshots/                 # Captured posts
├── main.py                      # Entry point
├── calibrate_osk.py             # OSK calibration tool
└── manual_reddit_test.py        # Manual testing
```

---

## 🎯 Common Commands

### Calibration
```bash
# First-time calibration (required!)
python calibrate_osk.py

# Re-calibrate after screen resolution change
python calibrate_osk.py
```

### Testing
```bash
# Test OSK typing
python tests/test_osk.py

# Test scrolling
python tests/test_scroll.py

# Test complete workflow
python tests/test_integration.py

# Manual Reddit test
python manual_reddit_test.py
```

### Running
```bash
# Immediate test run
python main.py

# View logs (real-time)
Get-Content logs\reddit_automation_*.log -Tail 50 -Wait
```

---

## ⚙️ Configuration Files

### Keywords (`config/keywords.yaml`)
```yaml
keywords:
  - term: "bull put spread"
    priority: high
    subreddits: [options, thetagang]
```

### Environment (`.env`)
```ini
ANTHROPIC_API_KEY=sk-ant-api03-your-key
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Scroll Settings (`config/scroll_settings.json`)
```json
{
  "scroll": {
    "step_size": 800,
    "max_scrolls_per_page": 10
  }
}
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| OSK won't launch | `taskkill /F /IM osk.exe` then retry |
| Calibration fails | Check Tesseract: `tesseract --version` |
| Typing doesn't work | Re-run: `python calibrate_osk.py` |
| Browser won't open | Update Chrome, reinstall selenium |
| LLM errors | Verify API key in `.env` |
| Scrolling stuck | Check browser window is focused |

---

## 🎮 How It Works

```
1. OSK Manager
   └─> Launches Windows On-Screen Keyboard
   └─> Clicks virtual keys to type text
   └─> NO physical keyboard used

2. Reddit Controller
   └─> Opens browser with mouse clicks only
   └─> Types URLs using OSK
   └─> Searches Reddit using OSK
   └─> Clicks tabs (Hot/New)

3. Scroll Controller
   └─> Uses mouse wheel to scroll
   └─> Detects end of infinite scroll
   └─> NO keyboard (Page Down, etc.)

4. Screenshot Engine
   └─> Captures Reddit posts
   └─> Excludes OSK from images
   └─> Prepares for LLM analysis

5. LLM Analyzer
   └─> Sends screenshots to Claude
   └─> Receives engagement decisions
   └─> Generates OSK-typeable comments

6. Scheduler
   └─> Runs daily at configured time
   └─> Processes all keywords
   └─> Logs results to Redis
```

---

## 📊 Key Metrics

| Metric | Value |
|--------|-------|
| OSK Typing Speed | ~1 char/second |
| Calibration Time | 30-60 seconds |
| Per-Keyword Processing | 5-10 minutes |
| Daily Run Duration | 1-2 hours (full list) |
| Screenshot Processing | 2-3 seconds/post |
| LLM Analysis | 5-10 seconds/post |

---

## 🚨 Critical Reminders

### ✅ Always Do This
- Calibrate OSK before first run
- Keep OSK visible during automation
- Run browser in non-headless mode (for OSK)
- Ensure screen resolution is 1920x1080
- Check logs after each run

### ❌ Never Do This
- Use keyboard input anywhere in code
- Move OSK after calibration
- Change screen resolution mid-run
- Run without calibration file
- Commit `.env` with API keys

---

## 📈 Performance Tips

### Speed Up Typing
```python
# src/osk_manager.py, line 79
self.key_delay = 0.05  # Faster (default: 0.1)
```

### Scroll Faster
```json
// config/scroll_settings.json
{
  "mouse_wheel": {
    "scroll_down_clicks": -5  // Default: -3
  }
}
```

### Process More Posts
```json
// config/scroll_settings.json
{
  "scroll": {
    "max_scrolls_per_page": 20  // Default: 10
  }
}
```

---

## 🔐 Security Checklist

- [ ] `.env` file in `.gitignore`
- [ ] Redis requires password
- [ ] API keys never in logs
- [ ] Screenshots auto-delete after 7 days
- [ ] File permissions restricted
- [ ] No hardcoded credentials

---

## 📞 Emergency Commands

### Kill Everything
```bash
# Kill browser
taskkill /F /IM chrome.exe

# Kill OSK
taskkill /F /IM osk.exe

# Kill Python
taskkill /F /IM python.exe
```

### Reset State
```bash
# Clear screenshots
del /Q screenshots\*

# Clear logs
del /Q logs\*

# Clear Redis
redis-cli FLUSHDB
```

### Fresh Start
```bash
# Re-calibrate
python calibrate_osk.py

# Test
python tests/test_integration.py

# Run
python main.py
```

---

## 🎯 Daily Workflow

### Morning Check (5 min)
1. Check last night's log: `logs/reddit_automation_*.log`
2. Verify run completed successfully
3. Check engagement stats in Redis

### Weekly Review (15 min)
1. Review keyword performance
2. Adjust priority in `config/keywords.yaml`
3. Update LLM prompts if needed
4. Clear old screenshots

### Monthly Maintenance (30 min)
1. Re-calibrate OSK
2. Update dependencies: `pip install --upgrade -r requirements.txt`
3. Review and optimize configuration
4. Backup calibration and config files

---

## 📝 Component Overview

| Component | Purpose | Key File |
|-----------|---------|----------|
| **OSK Manager** | Virtual keyboard clicking | `src/osk_manager.py` |
| **Scroll Controller** | Mouse wheel scrolling | `src/scroll_controller.py` |
| **Screenshot Engine** | Capture posts (exclude OSK) | `src/screenshot_engine.py` |
| **Reddit Controller** | Browser automation | `src/reddit_controller.py` |
| **LLM Analyzer** | Claude AI analysis | `src/llm_analyzer.py` |
| **Scheduler** | Daily automation | `src/scheduler.py` |

---

## 🔄 Workflow Diagram

```
START
  ↓
Launch OSK → Calibrate (if needed)
  ↓
Open Browser → Navigate to Reddit
  ↓
For Each Keyword:
  ├─> Search using OSK
  ├─> Click Hot/New tabs
  ├─> Scroll and capture posts
  ├─> Analyze with LLM
  └─> Engage (upvote/comment)
  ↓
Generate Report → Save to Redis
  ↓
Close Browser → Close OSK
  ↓
END
```

---

## 🌟 Best Practices

1. **Test First**: Always run `manual_reddit_test.py` before production
2. **Monitor Logs**: Check logs daily for errors
3. **Rate Limiting**: Respect Reddit API limits (built-in)
4. **Quality Over Quantity**: Focus on high-value keywords
5. **Review Comments**: Periodically review LLM-generated comments
6. **Backup Configs**: Keep backup of calibration and config files
7. **Stay Updated**: Update dependencies monthly

---

## 📧 Support

### Before Asking
- [x] Read README.md
- [x] Read DEPLOYMENT_GUIDE.md
- [x] Checked logs for errors
- [x] Ran tests: `python tests/test_integration.py`
- [x] Verified calibration exists

### Provide This Info
1. Python version: `python --version`
2. Installed packages: `pip list`
3. Error logs (last 50 lines)
4. Steps to reproduce
5. Expected vs actual behavior

---

**Happy Automating! 🎉**

For detailed information, see `DEPLOYMENT_GUIDE.md` and `README.md`.
