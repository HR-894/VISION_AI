# 👁️ VISION AI - Ultra-Fast Voice Assistant

> **Lightning-Fast, Pattern-Matching Voice Assistant for Windows**
> *Controlled via Push-to-Talk (Ctrl+Win) | Powered by Whisper*

![Status](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.13-blue) ![Speed](https://img.shields.io/badge/Response-<0.5s-orange)

## 🚀 What is VISION?
VISION AI is a **Lightning-Fast System Controller**. It uses pure pattern matching (no LLM) for instant command execution.
Voice recognition via Whisper, browser automation via Selenium, and regex-based command parsing for ultra-low latency.

## ⚙️ Whisper Model Configuration

Change accuracy in `vision_ai.py` line 17:
```python
WHISPER_SIZE = "base"  # Options below
```

**Available Models (ordered by accuracy):**
- `tiny` - Fastest, lowest accuracy (39M params, ~75MB) ⚡
- `base` - Balanced, good accuracy (74M params, ~142MB) ✅ **RECOMMENDED**
- `small` - Better accuracy (244M params, ~466MB)
- `medium` - High accuracy (769M params, ~1.5GB)
- `large-v3` - Best accuracy (1550M params, ~2.9GB) 🎯

**After changing, delete the cached model:**
```powershell
Remove-Item -Recurse -Force $env:USERPROFILE\.cache\huggingface\hub
```

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