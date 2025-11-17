# Reddit Automation System - Windows Server Edition

## 🚨 Critical: Zero Keyboard Access Environment

This system is designed for environments with **ZERO keyboard access** - streaming platforms, restricted terminals, or locked-down servers. All text input uses the **Virtual On-Screen Keyboard (OSK)** via mouse clicks, and all scrolling uses **mouse wheel events**.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Daily Automation Scheduler                  │
│         (Orchestrates all components on schedule)            │
└──────────────────────┬──────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       ▼               ▼               ▼
┌──────────┐   ┌─────────────┐   ┌──────────┐
│   OSK    │   │   Scroll    │   │Screenshot│
│ Manager  │   │ Controller  │   │  Engine  │
└─────┬────┘   └──────┬──────┘   └────┬─────┘
      │               │               │
      │    ┌──────────┴───────┐      │
      │    │                  │      │
      ▼    ▼                  ▼      ▼
┌─────────────────────────────────────────┐
│        Reddit Browser Controller         │
│   (Mouse-only navigation and search)     │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│       Options Edu LLM Integration        │
│    (Analyze posts, decide engagement)    │
└──────────────────────────────────────────┘
```

## 🎯 Core Components

### 1. OSK Manager (`osk_manager.py`)
- Launches Windows On-Screen Keyboard (OSK.exe)
- Auto-calibrates every key's screen coordinates
- Clicks virtual keys to type text
- Handles special characters, shift, backspace
- Saves calibration for future sessions

### 2. Scroll Controller (`scroll_controller.py`)
- Mouse wheel scrolling only (NO keyboard)
- Detects end of infinite scroll pages
- Coordinates with screenshot timing
- Tracks scroll position for recovery

### 3. Screenshot Engine (`screenshot_engine.py`)
- Captures Reddit posts while avoiding OSK
- Identifies post boundaries
- Maps clickable elements (upvote, comment)
- Prepares images for LLM analysis

### 4. Reddit Browser Controller (`reddit_controller.py`)
- Opens browser without keyboard shortcuts
- Types URLs using OSK
- Searches Reddit using OSK
- Clicks tabs and buttons
- Manages browser state

### 5. Options Edu LLM Integration (`llm_analyzer.py`)
- Sends screenshots to Options Edu API
- Receives engagement decisions
- Generates response text (OSK-compatible)
- Handles rate limiting

### 6. Daily Scheduler (`scheduler.py`)
- Runs monitoring on schedule
- Processes keyword lists
- Manages OSK lifecycle
- Generates reports
- Stores state in Redis

## 📋 Configuration Files

- `config/keywords.yaml` - Search terms and priorities
- `config/osk_calibration.json` - Key coordinate mappings
- `config/screen_coordinates.json` - Reddit UI element positions
- `config/llm_config.yaml` - API endpoints and settings
- `config/scroll_settings.json` - Scroll speeds and depths

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Tesseract OCR (for OSK calibration)
Download from: https://github.com/UB-Mannheim/tesseract/wiki
Add to PATH: `C:\Program Files\Tesseract-OCR`

### 3. Configure API Keys
```bash
cp .env.example .env
# Edit .env with your Options Edu LLM API key
```

### 4. Run Calibration (First Time)
```bash
python calibrate_osk.py
```
This launches OSK and maps every key's coordinates.

### 5. Test OSK Typing
```bash
python test_osk.py
```
Verifies that OSK clicking works correctly.

### 6. Run Manual Reddit Search
```bash
python manual_reddit_test.py
```
Tests complete flow: OSK typing → Search → Scroll → Screenshot

### 7. Start Daily Automation
```bash
python main.py
```

## 🔧 Manual Calibration Process

If auto-calibration fails, manually map key positions:

1. Launch OSK: `osk.exe`
2. Position at bottom of screen
3. Take screenshot
4. Open `config/osk_calibration.json`
5. For each key, note center coordinates
6. Update JSON with `{"key": [x, y]}` format

## ⚙️ Platform Requirements

- **OS**: Windows Server 2016+ or Windows 10+
- **Display**: 1920x1080 minimum resolution
- **RAM**: 4GB minimum (8GB recommended)
- **Browser**: Chrome/Chromium 100+
- **Python**: 3.9+
- **Redis**: 6.0+ (for state management)

## 🎮 Operational Constraints

### ✅ What Works
- Mouse clicking at any screen coordinate
- Mouse wheel scrolling (up/down)
- OSK key clicking for text input
- Screenshot capture
- Browser automation via mouse
- Triple-click text selection

### ❌ What Doesn't Work (Disabled)
- Keyboard typing (NO physical keyboard)
- Keyboard shortcuts (Ctrl+C, Ctrl+V, etc.)
- Hotkeys (F5, Tab, Enter via keyboard)
- Clipboard paste (Ctrl+V blocked)
- Any keyboard-based automation

## 📊 Performance Expectations

- **OSK Typing Speed**: ~1 character/second
- **Calibration Time**: 30-60 seconds (first run)
- **Per-Keyword Processing**: 5-10 minutes
- **Daily Run Duration**: 1-2 hours for full keyword list
- **Screenshot Processing**: 2-3 seconds/capture
- **LLM Analysis**: 5-10 seconds/post

## 🛠️ Troubleshooting

### OSK Not Launching
```bash
# Manual launch
osk.exe

# Check if already running
tasklist | findstr osk
```

### Calibration Fails
- Ensure OSK is visible and not minimized
- Check screen resolution is 1920x1080
- Verify Tesseract is installed and in PATH
- Try manual calibration process

### Typing Not Working
- Re-run calibration
- Check OSK is in foreground
- Verify coordinates in `osk_calibration.json`
- Test with `test_osk.py`

### Scrolling Issues
- Ensure browser window is in focus
- Check mouse wheel settings in Windows
- Verify `scroll_settings.json` values
- Test with `test_scroll.py`

## 📁 Project Structure

```
windowsGUISessionAutomation/
├── config/
│   ├── keywords.yaml
│   ├── osk_calibration.json
│   ├── screen_coordinates.json
│   ├── llm_config.yaml
│   └── scroll_settings.json
├── src/
│   ├── osk_manager.py
│   ├── scroll_controller.py
│   ├── screenshot_engine.py
│   ├── reddit_controller.py
│   ├── llm_analyzer.py
│   └── scheduler.py
├── tests/
│   ├── test_osk.py
│   ├── test_scroll.py
│   ├── test_screenshot.py
│   └── test_integration.py
├── logs/
│   └── (daily logs)
├── screenshots/
│   └── (captured posts)
├── calibrate_osk.py
├── manual_reddit_test.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🔒 Security Considerations

- API keys stored in `.env` (never commit)
- Redis requires authentication
- Screenshots contain sensitive data (auto-delete after 7 days)
- LLM requests logged (review for PII)

## 📝 Logging

All actions logged to `logs/reddit_automation_YYYYMMDD.log`:
- OSK key clicks with coordinates
- Scroll positions and distances
- Screenshot captures
- LLM API calls and responses
- Engagement actions taken
- Errors and recovery attempts

## 🎯 Success Metrics

- **Typing Accuracy**: >95% OSK click success
- **Scroll Reliability**: 100% (no keyboard required)
- **Uptime**: >99% during scheduled runs
- **Engagement Success**: >90% actions executed
- **Recovery Time**: <30 seconds from failures

## 📞 Support

For issues or questions, check:
1. Logs in `logs/` directory
2. Calibration data in `config/`
3. Test scripts in `tests/`
4. GitHub Issues (if applicable)

## 🚀 Future Enhancements

- Multi-monitor support
- Alternative virtual keyboards (TabTip.exe)
- Browser extension integration
- Mobile browser emulation
- Advanced OCR for Reddit UI detection
- Machine learning for coordinate adaptation
