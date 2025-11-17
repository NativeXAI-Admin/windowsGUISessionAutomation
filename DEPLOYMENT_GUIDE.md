# Deployment Guide - Windows Server

## 🚀 Complete Installation Guide

### Prerequisites

#### 1. Windows Server Setup
- **OS**: Windows Server 2016+ or Windows 10+
- **Display**: 1920x1080 resolution (required for OSK calibration)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 10GB free space
- **Python**: 3.9 or higher

#### 2. Install Python
```bash
# Download Python 3.9+ from python.org
# During installation, check "Add Python to PATH"

# Verify installation
python --version
pip --version
```

#### 3. Install Tesseract OCR
Required for OSK calibration (key position detection):

1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (use default location: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH:
   - Open System Properties → Environment Variables
   - Edit PATH, add: `C:\Program Files\Tesseract-OCR`
   - Verify: `tesseract --version`

#### 4. Install Redis (Optional but Recommended)
For state persistence between runs:

1. Download Redis for Windows: https://github.com/tporadowski/redis/releases
2. Extract to `C:\Redis`
3. Run `redis-server.exe` or install as Windows service
4. Test: `redis-cli ping` (should return "PONG")

#### 5. Install Google Chrome
Required for browser automation:

1. Download from: https://www.google.com/chrome/
2. Install to default location
3. Verify installation

---

## 📦 Project Installation

### Step 1: Clone/Download Project
```bash
cd C:\
mkdir RedditAutomation
cd RedditAutomation
# Copy all project files here
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Or activate (PowerShell)
venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Common Installation Issues**:

- **OpenCV Error**: `pip install opencv-python-headless` (if headless server)
- **Anthropic Error**: `pip install --upgrade anthropic`
- **Redis Error**: Ensure Redis server is running

### Step 4: Configure Environment
```bash
# Copy example env file
copy .env.example .env

# Edit .env with your API keys
notepad .env
```

**Required Configuration**:
```ini
ANTHROPIC_API_KEY=sk-ant-api03-your-api-key-here
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
```

### Step 5: Initial Calibration
**CRITICAL FIRST STEP** - Calibrate the On-Screen Keyboard:

```bash
python calibrate_osk.py
```

This will:
1. Launch Windows OSK
2. Detect key positions using OCR
3. Save calibration to `config/osk_calibration.json`
4. Test typing functionality

**Calibration Tips**:
- Ensure screen resolution is 1920x1080
- Position OSK at bottom of screen when prompted
- Do NOT move OSK after calibration
- Re-calibrate if screen resolution changes

---

## ✅ Verification Tests

### Test 1: OSK Functionality
```bash
python tests/test_osk.py
```
Expected: All tests pass, typing works in text fields

### Test 2: Scroll Controller
```bash
python tests/test_scroll.py
```
Expected: Mouse wheel scrolling works without keyboard

### Test 3: Manual Reddit Test
```bash
python manual_reddit_test.py
```
Expected:
- Browser opens
- Navigates to Reddit using OSK
- Searches for keywords
- Scrolls and captures posts

### Test 4: Integration Test
```bash
python tests/test_integration.py
```
Expected: Complete workflow executes successfully

---

## 🎮 Running the System

### Option 1: Immediate Test Run
```bash
python main.py
```
This runs once immediately (for testing).

### Option 2: Scheduled Daily Runs

Edit `src/scheduler.py` line 348:
```python
# Uncomment these lines:
# logger.info("\n📅 Scheduling daily runs at 09:00...")
# scheduler.schedule_daily_run(run_time="09:00")
```

Then run:
```bash
python main.py
```
System will run at 09:00 daily.

### Option 3: Windows Task Scheduler

For production, use Windows Task Scheduler:

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Reddit Automation"
4. Trigger: Daily at 09:00 AM
5. Action: Start a program
   - Program: `C:\RedditAutomation\venv\Scripts\python.exe`
   - Arguments: `C:\RedditAutomation\main.py`
   - Start in: `C:\RedditAutomation`
6. Save and test

---

## 🔧 Configuration Tuning

### Adjust Keyword List
Edit `config/keywords.yaml`:
```yaml
keywords:
  - term: "your keyword"
    priority: high
    subreddits:
      - options
```

### Adjust Scroll Settings
Edit `config/scroll_settings.json`:
```json
{
  "scroll": {
    "step_size": 800,
    "max_scrolls_per_page": 10
  }
}
```

### Adjust LLM Settings
Edit `config/llm_config.yaml`:
```yaml
api:
  model: "claude-sonnet-4-5-20250929"
  max_tokens: 1024
  temperature: 0.3
```

---

## 📊 Monitoring and Logs

### Log Locations
- **Main logs**: `logs/reddit_automation_*.log`
- **Calibration**: `logs/calibration.log`
- **Tests**: `logs/test_*.log`

### View Logs (Real-time)
```bash
# Windows PowerShell
Get-Content logs\reddit_automation_*.log -Tail 50 -Wait

# Windows CMD
type logs\reddit_automation_*.log
```

### Daily Statistics
Check Redis for stored run statistics:
```bash
redis-cli
> KEYS reddit_scan:*
> GET reddit_scan:2025-11-16
```

---

## 🐛 Troubleshooting

### OSK Won't Launch
```bash
# Check if OSK is already running
tasklist | findstr osk

# Kill existing OSK
taskkill /F /IM osk.exe

# Try launching manually
osk.exe
```

### Calibration Fails
1. Ensure Tesseract is in PATH: `tesseract --version`
2. Check screen resolution: 1920x1080 required
3. Try manual calibration:
   - Launch OSK manually
   - Take screenshot
   - Manually edit `config/osk_calibration.json`

### Typing Not Working
1. Re-run calibration: `python calibrate_osk.py`
2. Check OSK is visible during typing
3. Verify coordinates in `config/osk_calibration.json`
4. Test with `tests/test_osk.py`

### Browser Won't Open
1. Check Chrome is installed
2. Install ChromeDriver: `pip install webdriver-manager`
3. Update selenium: `pip install --upgrade selenium`

### LLM Errors
1. Verify API key in `.env`
2. Check network connectivity
3. Test API manually:
```python
from anthropic import Anthropic
client = Anthropic(api_key="your-key")
print(client.messages.create(...))
```

### Scrolling Issues
1. Ensure browser window is focused
2. Check mouse wheel settings in Windows
3. Test with `tests/test_scroll.py`

---

## 🔒 Security Best Practices

### 1. Secure API Keys
```bash
# Never commit .env file
echo .env >> .gitignore

# Use environment variables in production
set ANTHROPIC_API_KEY=your-key
```

### 2. Restrict File Permissions
```bash
# Windows: Right-click .env → Properties → Security
# Set permissions to "Read" only for current user
```

### 3. Redis Authentication
Edit Redis config (`redis.windows.conf`):
```
requirepass your-strong-password
```

### 4. Screenshot Cleanup
System auto-deletes screenshots after 7 days.
Adjust in `.env`:
```
SCREENSHOT_AUTO_DELETE_DAYS=7
```

---

## 🚀 Performance Optimization

### 1. Reduce Typing Delay
Edit `src/osk_manager.py` line 79:
```python
self.key_delay = 0.05  # Faster (default: 0.1)
```

### 2. Increase Scroll Speed
Edit `config/scroll_settings.json`:
```json
{
  "mouse_wheel": {
    "scroll_down_clicks": -5  # Faster (default: -3)
  }
}
```

### 3. Adjust LLM Rate Limits
Edit `config/llm_config.yaml`:
```yaml
rate_limits:
  requests_per_minute: 30  # Higher (default: 20)
```

---

## 📈 Scaling Up

### Process More Keywords
Edit `config/keywords.yaml` to add more search terms.

### Multi-Subreddit Search
```yaml
keywords:
  - term: "iron condor"
    subreddits:
      - options
      - thetagang
      - wallstreetbets
```

### Increase Scroll Depth
Edit `config/scroll_settings.json`:
```json
{
  "scroll": {
    "max_scrolls_per_page": 20  # More posts (default: 10)
  }
}
```

---

## 🔄 Maintenance Schedule

### Daily
- Check logs for errors: `logs/reddit_automation_*.log`
- Verify daily run completed successfully

### Weekly
- Review engagement statistics in Redis
- Check screenshot storage: `screenshots/`
- Update keyword list if needed

### Monthly
- Re-calibrate OSK if needed
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Review and optimize LLM prompts

---

## 📞 Support Checklist

Before requesting support, gather:

1. **System Info**:
   ```bash
   python --version
   pip list
   systeminfo
   ```

2. **Logs**:
   - Latest `logs/reddit_automation_*.log`
   - Calibration log if applicable

3. **Configuration**:
   - `.env` (sanitize API keys!)
   - `config/osk_calibration.json`

4. **Error Details**:
   - Full error message
   - Steps to reproduce
   - Expected vs actual behavior

---

## ✅ Production Deployment Checklist

- [ ] Python 3.9+ installed
- [ ] Tesseract OCR installed and in PATH
- [ ] Redis installed and running
- [ ] Chrome browser installed
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] API keys configured in `.env`
- [ ] OSK calibrated: `python calibrate_osk.py`
- [ ] Tests passing: `python tests/test_integration.py`
- [ ] Logs directory created and writable
- [ ] Screenshots directory created
- [ ] Windows Task Scheduler configured (for daily runs)
- [ ] Monitoring alerts configured
- [ ] Backup strategy in place

---

## 🎯 Quick Start Commands

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
copy .env.example .env
notepad .env

# 3. Calibrate OSK
python calibrate_osk.py

# 4. Test
python tests/test_integration.py

# 5. Run
python main.py
```

---

**System ready! 🎉**

For daily automated runs, configure Windows Task Scheduler or edit `src/scheduler.py` to enable scheduled execution.
