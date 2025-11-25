
---

## 🚀 What is VISION AI?

**VISION AI** is a **blazing-fast, offline-capable voice assistant** designed for Windows power users. Unlike bloated AI assistants that require internet and cloud processing, VISION AI:

- ⚡ **Executes commands instantly** using pure pattern matching (no AI inference delays)
- 🎤 **Recognizes voice offline** via Whisper (Hugging Face)
  
- **Browser Automation**: Intelligent YouTube search with Selenium
  - `browse dhruv rathee youtube` - Opens YouTube and searches
  - `search coding tutorial yt` - Alternative syntax
  - Persistent browser session (no repeated Chrome launches)

- **Web Shortcuts**: Quick access to common sites
  - `open github`, `open gmail`, `open reddit`
  - `search python tutorials` - Google search

- **System Info**: On-demand stats
  - `cpu` - Show CPU usage
  - `ram` - Show memory usage
  - `time` / `date` - Current time/date

### Prerequisites
- **Windows 10/11** (64-bit)
- **Python 3.10+** (Tested on Python 3.13)
- **Git** (optional, for cloning)

### Quick Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/HR-894/VISION_AI.git
   cd VISION_AI
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run VISION AI**
   ```bash
   python vision_ai.py
   ```
   Or double-click `Run_VISION.bat`

---

## ⚙️ Configuration

### Whisper Model Selection

Edit `vision_ai.py` (line 17) to change voice recognition accuracy:

```python
WHISPER_SIZE = "base"  # Change this
```

| Model | Speed | Accuracy | Size | Use Case |
|-------|-------|----------|------|----------|
| `tiny` | ⚡⚡⚡⚡⚡ | ⭐⭐ | 75MB | Ultra-fast, noisy environments |
| `base` | ⚡⚡⚡⚡ | ⭐⭐⭐ | 142MB | ✅ **Recommended** - Balanced |
| `small` | ⚡⚡⚡ | ⭐⭐⭐⭐ | 466MB | Better accuracy |
| `medium` | ⚡⚡ | ⭐⭐⭐⭐⭐ | 1.5GB | High accuracy |
| `large-v3` | ⚡ | ⭐⭐⭐⭐⭐⭐ | 2.9GB | Best accuracy |

**Clear cached models after changing:**
```powershell
Remove-Item -Recurse -Force $env:USERPROFILE\.cache\huggingface\hub
```

### Hotkey Customization

1. Click **Settings** button in app
2. Enter new hotkey (e.g., `ctrl+shift+space`)
3. Click **Save**

---

## 🎮 Usage Examples

### Voice Commands
Hold `Ctrl+Windows` and speak:

**Launch Apps:**
- "Open Chrome"
- "Open Zoom Workplace"
- "Open Windows Settings"
- "Launch Spotify"

**Browse Web:**
- "Browse Carryminati YouTube"
- "Search Python tutorial on YT"
- "Open GitHub"

**System Info:**
- "CPU"
- "RAM"
- "Time"

### Text Commands
Type in the input box:
├── requirements.txt      # Python dependencies
├── Run_VISION.bat        # Quick launcher script
├── setup_vision.py       # Setup helper
├── VISION_AI.spec        # PyInstaller build spec
├── README.md             # This file
└── .gitignore            # Git exclusions
```

---

## 🔧 Advanced Features

### Microsoft Store (UWP) App Support
VISION AI uses PowerShell `Get-StartApps` to resolve UWP app IDs:
```python
# Automatically handles:
- Zoom Workplace
- WhatsApp (desktop)
- Spotify (Store version)
- Any installed Store app
```

### Selenium Browser Automation
- Persistent Chrome session (reuses same browser window)
- Auto-recovery from session crashes
- Configurable options in `automate_youtube()` method

### Pattern Matching Engine
Zero AI inference for instant responses:
- Regex-based command parsing
- 20+ app shortcuts with aliases
- 10+ URL shortcuts
- Extensible command system

---

## 🚧 Building Executable

Create a standalone `.exe` (no Python required):

```bash
pyinstaller VISION_AI.spec
```

Output: `dist/VISION_AI.exe`

---

## 📝 Dependencies

- **customtkinter** - Modern UI framework
- **faster-whisper** - Offline voice recognition
- **sounddevice** - Audio capture
- **selenium** - Browser automation
- **pystray** - System tray integration
- **keyboard** - Hotkey monitoring
- **psutil** - System stats

See `requirements.txt` for full list.

---

## 🐛 Troubleshooting

### App not opening?
- **Microsoft Store apps**: Ensure app is installed and visible in Start menu
- **Desktop apps**: Check if `.exe` is in system PATH
- **Zoom**: VISION AI checks both classic and UWP versions

### YouTube search not working?
- Requires **Chrome** browser installed
- First search downloads ChromeDriver (~10MB)
- Check internet connection for Selenium WebDriver

### Voice not recognized?
- Speak clearly after beep sound
- Hold `Ctrl+Windows` during entire phrase
- Try larger Whisper model (`small` or `medium`)
- Check microphone permissions in Windows Settings

### High CPU usage?
- Default `base` model uses ~200MB RAM
- Switch to `tiny` model for lower resource usage
- Close background apps during voice recognition

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Add more app shortcuts
- [ ] Support custom command macros
- [ ] Multi-language support (Whisper supports 99 languages)
- [ ] Plugin system for extensibility
- [ ] Cross-platform support (Linux/macOS)

---

## 📜 License

MIT License - See LICENSE file for details.

---

## 👨‍💻 Author

**HIMANSHU (HR-894)**  
GitHub: [@HR-894](https://github.com/HR-894)

---

## 🌟 Star This Repo!

If you find VISION AI useful, please ⭐ this repository and share with friends!

**Built with ❤️ for Windows power users**

### ✨ Key Features
- **Ghost Mode:** Minimizes to System Tray, always ready.
- **Universal Launcher:** Open *any* app just by saying its name ("Open Excel", "Open Spotify").
- **Web Intelligence:** Smart enough to open websites ("Open youtube.com").
- **Privacy Core:** 0% Data leaves your device. Everything runs on localhost.

---

## 🛠️ Installation (For Developers)

If you want to run the code manually, follow these steps strictly to avoid errors.

### Prerequisites
1. **Python 3.10+** installed.
2. **Git** installed.

### Step-by-Step Setup

1. **Clone the Repo:**
   ```bash
   git clone [https://github.com/HR-894/vision-ai.git](https://github.com/HR-894/vision-ai.git)
   cd vision-ai

2. Install Dependencies (The Right Way): Run this EXACT command to avoid C++ Build Tools errors:
   ```bash
   pip install llama-cpp-python --extra-index-url [https://abetlen.github.io/llama-cpp-python/whl/cpu](https://abetlen.github.io/llama-cpp-python/whl/cpu)

Then install the rest:
   ```bash
   pip install faster-whisper pystray Pillow sounddevice keyboard psutil scipy numpy pyinstaller
   
3. Download the Brain (Model): Create a folder named models and run this command:
   ```bashPowerShell
   mkdir models
   curl -L -o models/Llama-3.2-1B-Instruct-Q4_K_M.gguf "[https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf?download=true](https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf?download=true)"

4. Run the Assistant: Double click Run_VISION.bat OR run:
   ```bash
   python vision_ai.py

 🎮 How to Use

App will launch and minimize to System Tray (near clock).

Hold Ctrl + Windows key.

Speak your command (e.g., "Open Notepad", "Search Tesla stock").

Release keys. Watch the magic! ✨

🏗️ Build EXE (Create Standalone App)

To create a shareable .exe file for friends:
```bash
pyinstaller --noconfirm --onefile --windowed --name "VISION_AI" --icon "NONE" --add-data "models;models" --collect-all "llama_cpp" --collect-all "faster_whisper" --collect-all "sounddevice" --collect-all "keyboard" --collect-all "psutil" --hidden-import="pystray" --hidden-import="PIL" vision_ai.py

The output file will be in the dist folder.

Built with ❤️ by HIMANSHU ~HR-894