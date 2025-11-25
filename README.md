# 👁️ VISION AI

**Your Intelligent AI Voice & Text Assistant for Windows**

100% Local • Privacy-First • Adaptive AI • Multi-Step Planning

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

---

## 🌟 Features

- 🎤 **Voice Commands** - Whisper AI (90-95% accuracy)
- 🧠 **LLM Planning** - Multi-step task automation with Llama
- 🔒 **100% Private** - All AI runs locally on YOUR device
- ⚡ **Adaptive Performance** - Auto-optimizes for your hardware
- 🧠 **Smart Memory** - Learns from your commands
- 🌐 **Web Search** - DuckDuckGo integration (optional)
- 📂 **File Management** - List, search, open files
- 🎬 **YouTube Automation** - Voice-controlled browsing
- 🪟 **Window Controls** - Manage apps, take screenshots
- 💻 **System Monitoring** - CPU, RAM, and more

---

## 📋 Requirements

### Minimum System Requirements
- **OS:** Windows 10/11 (64-bit)
- **RAM:** 4GB (8GB+ recommended)
- **Storage:** 2GB free space
- **Python:** 3.10 or higher (for running from source)

### For .exe Distribution (No Python needed!)
- Just Windows 10/11 64-bit
- 2GB free space

---

## 🚀 Quick Start (Using .exe)

### Option 1: Pre-built Executable

1. **Download** the `VISION_AI.zip` from releases
2. **Extract** to any folder
3. **Download Models** (first time only):
   ```powershell
   # Create models folder
   cd VISION_AI
   mkdir models
   
   # Download Llama model (770MB)
   # Visit: https://huggingface.co/TheBloke/Llama-3.2-1B-Instruct-GGUF
   # Download: Llama-3.2-1B-Instruct-Q4_K_M.gguf
   # Place in: models/
   ```
4. **Run** `VISION_AI.exe`

**First launch will:**
- Detect your hardware
- Load Whisper model (auto-download ~1GB)
- Initialize LLM
- Start GUI (~30 seconds total)

---

## 🛠️ Installation (From Source)

### Step 1: Clone Repository

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/VISION_AI.git
cd VISION_AI
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.venv\Scripts\activate.bat

# Activate (Git Bash)
source .venv/Scripts/activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# This installs:
# - customtkinter (GUI)
# - faster-whisper (voice recognition)
# - llama-cpp-python (LLM)
# - selenium (automation)
# - and 15+ other packages
```

### Step 4: Download AI Models

```bash
# Create models directory
mkdir models

# Download Llama-3.2-1B model (770MB)
# Manual download required from:
# https://huggingface.co/TheBloke/Llama-3.2-1B-Instruct-GGUF/blob/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf

# Or use wget (if installed):
wget -P models/ https://huggingface.co/TheBloke/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf
```

**Model Storage:**
```
VISION_AI/
└── models/
    └── Llama-3.2-1B-Instruct-Q4_K_M.gguf  (770MB)
```

**Note:** Whisper model auto-downloads on first run (~1GB)

### Step 5: Run Application

```bash
# Make sure virtual environment is activated
python vision_ai.py
```

---

## 🎯 Usage

### Voice Commands
1. Hold `Ctrl+Windows` key
2. Speak your command
3. Release key when done

### Text Commands
- Type in the input box
- Press Enter or click Send
- Use ↑↓ for command history

### Example Commands

**File Operations:**
```
list downloads
open C:\Users\YourName\Documents\file.txt
open %USERPROFILE%\Desktop
find *.pdf
```

**Apps & Web:**
```
open chrome
open notepad
search python tutorial
youtube physics lectures
```

**YouTube (Context-Aware):**
```
browse quantum physics youtube
play first video
next video
pause
```

**Multi-Step (LLM Planning):**
```
list downloads to google keep
open notepad and write hello world
```

**System:**
```
cpu
ram
screenshot
volume 50
time
```

---

## 🏗️ Building Executable

Want to create your own `.exe` file?

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable (this takes ~5 minutes)
pyinstaller --onedir --noconsole --name="VISION_AI" --clean vision_ai.py

# Output will be in:
# dist/VISION_AI/
# ├── VISION_AI.exe (8.92 MB)
# └── _internal/ (279 MB)
```

**To distribute:**
1. Zip the entire `dist/VISION_AI/` folder
2. Share the ZIP file (~288 MB compressed)
3. Users extract and run `VISION_AI.exe`
4. Users need to download models separately

---

## 📦 Distribution Guide

### For Friends/Users:

**Package Contents:**
```
VISION_AI/
├── VISION_AI.exe          (Main app - 8.92 MB)
├── _internal/             (Dependencies - 279 MB)
│   ├── Python runtime
│   ├── AI libraries
│   └── System files
└── models/                (User must download)
    └── Llama-3.2-1B-Instruct-Q4_K_M.gguf
```

**Share:**
- ✅ `VISION_AI.exe` 
- ✅ `_internal/` folder
- 📝 Link to model download

**Users need BOTH .exe and _internal folder!**

---

## 🧪 Testing

Run automated test suite:

```bash
# Create test file (if not exists)
# test_suite.py should be in repo

# Run tests
python test_suite.py

# Expected output:
# Total Tests: 33
# Passed: 33
# Success Rate: 100%
```

---

## 🔧 Troubleshooting

### "DLL load failed" or "Module not found"
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Whisper Model Download Fails
```bash
# Manual download alternative
# Visit: https://huggingface.co/guillaumekln/faster-whisper-medium
# Or use different size: base, small, medium, large-v3
```

### LLM Model Not Found
```bash
# Check models folder exists
ls models/

# Verify filename exactly matches:
# Llama-3.2-1B-Instruct-Q4_K_M.gguf
```

### Microphone Not Working
- Check Windows microphone permissions
- Try different hotkey in Settings
- Ensure no other app is using microphone

### High RAM Usage
- Normal for LOW-END: 400-600 MB
- Normal for HIGH-END: 800-1200 MB
- App auto-adapts to your hardware

---

## 📚 Project Structure

```
VISION_AI/
├── vision_ai.py                 # Main application
├── context_manager.py           # Context awareness
├── safety_guard.py              # Command validation
├── file_manager.py              # File operations
├── window_manager.py            # Window controls
├── llm_controller.py            # LLM integration
├── action_executor.py           # Action execution
├── smart_template_matcher.py   # Pattern matching
├── fast_complex_handler.py     # Complex commands
├── agent_memory.py             # Command learning
├── web_search.py               # Web integration
├── device_profiler.py          # Hardware detection
├── requirements.txt            # Dependencies
├── README.md                   # This file
└── models/                     # AI models
    └── Llama-3.2-1B-Instruct-Q4_K_M.gguf
```

---

## 🔐 Privacy

**100% Local AI Processing:**
- ✅ Voice recognition (Whisper) - runs locally
- ✅ LLM planning (Llama) - runs locally
- ✅ Command history - stored locally only
- ✅ No telemetry or data collection

**Optional Internet Usage:**
- 🌐 Web search (DuckDuckGo) - only when you use search commands
- 🌐 YouTube automation - only when you browse YouTube
- 🌐 Model downloads - one-time initial setup

See [PRIVACY.md](PRIVACY.md) for full details.

---

## 🤝 Contributing

Contributions are welcome! 

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Whisper** - OpenAI (via faster-whisper)
- **Llama** - Meta AI (via llama-cpp-python)
- **CustomTkinter** - TomSchimansky
- **Selenium** - SeleniumHQ
- All other open-source contributors

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/VISION_AI/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_USERNAME/VISION_AI/discussions)

---

## 🚀 Roadmap

- [x] Voice recognition (Whisper)
- [x] LLM planning (Llama)
- [x] Adaptive performance
- [x] Memory system
- [x] Web search
- [ ] Computer vision (PaddleOCR)
- [ ] Multi-monitor support
- [ ] Plugin system
- [ ] Cloud sync (optional)

---

**Made with ❤️ for productivity and privacy**

*VISION AI - See what's possible with local AI*