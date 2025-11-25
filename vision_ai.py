import customtkinter as ctk
import sys, os, threading, json, keyboard, re, subprocess
import sounddevice as sd
import numpy as np
import winsound, psutil, gc
from faster_whisper import WhisperModel
import pystray
from PIL import Image, ImageDraw
from datetime import datetime

# Import new agentic modules
from context_manager import ContextManager
from safety_guard import SafetyGuard
from file_manager import FileManager
from window_manager import WindowManager
from llm_controller import LLMController
from action_executor import ActionExecutor
from fast_complex_handler import FastComplexHandler
from smart_template_matcher import SmartTemplateMatcher
from agent_memory import AgentMemory
from web_search import WebSearch
from device_profiler import DeviceProfiler

# --- Config ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Auto-detect device and configure optimal models
DEVICE_PROFILER = DeviceProfiler()
OPTIMAL_MODELS = DEVICE_PROFILER.get_optimal_models()
PERF_CONFIG = DEVICE_PROFILER.get_performance_config()

WHISPER_SIZE = OPTIMAL_MODELS['whisper']  # Adaptive: medium/large-v3 based on device
DEFAULT_HOTKEY = "ctrl+windows"
CONFIG_FILE = os.path.join(BASE_DIR, "vision_config.json")

# App shortcuts with aliases
APP_SHORTCUTS = {
    "chrome": "chrome.exe", "browser": "chrome.exe",
    "notepad": "notepad.exe", "note": "notepad.exe",
    "calculator": "calc.exe", "calc": "calc.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe", "files": "explorer.exe",
    "cmd": "cmd.exe", "terminal": "cmd.exe", "command": "cmd.exe",
    "powershell": "powershell.exe", "ps": "powershell.exe",
    "word": "winword.exe", "msword": "winword.exe",
    "excel": "excel.exe", "msexcel": "excel.exe",
    "vscode": "code.exe", "vs code": "code.exe", "code": "code.exe",
    "spotify": "spotify.exe", "music": "spotify.exe",
    "discord": "discord.exe", "zoom": "zoom.exe",
    "teams": "teams.exe", "slack": "slack.exe",
    "outlook": "outlook.exe", "mail": "outlook.exe",
    "whatsapp": "whatsapp.exe", "wa": "whatsapp.exe"
}

# URL shortcuts
URL_SHORTCUTS = {
    "youtube": "youtube.com", "yt": "youtube.com",
    "gmail": "gmail.com", "mail": "gmail.com",
    "github": "github.com", "git": "github.com",
    "twitter": "twitter.com", "x": "x.com",
    "facebook": "facebook.com", "fb": "facebook.com",
    "linkedin": "linkedin.com", "reddit": "reddit.com",
    "whatsapp": "web.whatsapp.com", "wa": "web.whatsapp.com"
}

class VisionAI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.config = self.load_config()
        self.hotkey = self.config.get("hotkey", DEFAULT_HOTKEY)
        
        try:
            p = psutil.Process(os.getpid())
            p.nice(psutil.HIGH_PRIORITY_CLASS)
        except:
            pass

        self.title("VISION AI")
        self.geometry("900x700")
        ctk.set_appearance_mode("Dark")
        
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
        # Initialize core modules
        self.context = ContextManager()
        self.safety = SafetyGuard()
        self.file_mgr = FileManager(self.safety)  # Pass safety_guard
        self.window_mgr = WindowManager()
        
        # LLM Controller with adaptive model selection
        llm_model = OPTIMAL_MODELS['llm']
        llm_filename = f"{llm_model.replace('.', '-').replace(' ', '-')}-Q4_K_M.gguf"
        model_path = os.path.join(BASE_DIR, "models", llm_filename)
        
        # Fallback to Llama-3.2-1B if selected model doesn't exist
        if not os.path.exists(model_path):
            model_path = os.path.join(BASE_DIR, "models", "Llama-3.2-1B-Instruct-Q4_K_M.gguf")
        
        self.llm = LLMController(model_path)
        self.device_tier = DEVICE_PROFILER.tier
        self.executor = ActionExecutor(self)
        
        # Initialize handlers
        self.smart_templates = SmartTemplateMatcher(self)
        self.fast_complex = FastComplexHandler(self)
        
        # Initialize Phase 1: Memory & Web Intelligence
        self.memory = AgentMemory()
        self.web_search = WebSearch()
        
        # Initialize state variables
        self.browser = None
        self.command_history = []
        self.history_index = 0
        self.last_response = ""
        self.tray_icon = None
        self.is_recording = False
        self.audio_data = []
        
        # Setup UI
        self.setup_ui()
        
        # Start background threads
        self.add_message("System", "🚀 Initializing VISION Core...")
        threading.Thread(target=self.load_models, daemon=True).start()
        threading.Thread(target=self.listen_for_hotkey, daemon=True).start()
        threading.Thread(target=self.update_system_stats, daemon=True).start()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"hotkey": DEFAULT_HOTKEY}

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except:
            pass

    def use_preset(self, preset_type):
        """Insert preset command template into input field"""
        templates = {
            "open": "open ",
            "browse": "browse ",
            "search": "search "
        }
        self.text_input.delete(0, 'end')
        self.text_input.insert(0, templates.get(preset_type, ""))
        self.text_input.focus()
    
    def show_help(self):
        """Show comprehensive help dialog"""
        help_window = ctk.CTkToplevel(self)
        help_window.title("VISION AI - Help & Instructions")
        help_window.geometry("700x600")
        help_window.transient(self)
        help_window.grab_set()
        
        # Header
        ctk.CTkLabel(help_window, text="❓ How to Use VISION AI", font=("Segoe UI", 22, "bold"), text_color="#00ccff").pack(pady=15)
        
        # Scrollable content
        help_scroll = ctk.CTkScrollableFrame(help_window, width=650, height=450)
        help_scroll.pack(padx=20, pady=10, fill="both", expand=True)
        
        help_text = """
🎯 OVERVIEW:
VISION AI is your voice & text command assistant. Lightning-fast pattern matching for instant actions!

⌨️ INPUT METHODS:
• Type commands in the text box and press Enter
• Hold '{hotkey}' and speak your command
• Use ↑↓ arrow keys to browse command history

⚡ QUICK PRESETS:
• 📂 Open - Opens apps, files, or websites
• 🔍 Browse - Browse content on YouTube or web
• 🌐 Search - Search Google for anything

📂 OPEN COMMANDS:
• "open chrome" - Launch Chrome browser
• "open notepad" - Open Notepad
• "open calculator" / "calc" - Open Calculator
• "open vscode" / "code" - Launch VS Code
• "open youtube.com" - Open any website
• "open zoom" - Launch Zoom (or any installed app)
• "open windows settings" - Open Windows Settings

🎥 YOUTUBE AUTOMATION:
• "browse dhruv rathee youtube" - Searches YouTube
• "search coding tutorial yt" - Searches YouTube for coding tutorial
• "play lofi music youtube" - Plays lofi music on YouTube
• Works with both "youtube" and "yt" keywords

🔍 GOOGLE SEARCH:
• "search python tutorial" - Google search
• "google artificial intelligence" - Google search
• "find best restaurants near me" - Google search

🌐 QUICK WEBSITE ACCESS:
• Just type: "youtube" / "yt" / "gmail" / "github" / "twitter"
• Instantly opens the website

📊 SYSTEM INFORMATION:
• "cpu" / "processor" - Show CPU usage
• "ram" / "memory" - Show RAM usage
• "time" - Current time
• "date" - Current date

⚙️ APP CONTROLS:
• "settings" / "config" - Open VISION settings
• "clear" - Clear chat history
• "copy" - Copy last response

🔗 CHAINED COMMANDS:
• Combine multiple actions with "and" or "then"
• VISION intelligently separates commands from queries
• "open chrome and search gravity" → Opens Chrome, then searches
• "search gravity and newton" → Searches for "gravity and newton"
• "open notepad and write list of downloads" → Opens Notepad, then writes list

🎤 VOICE INPUT:
• Hold '{hotkey}' key
• Speak your command clearly
• Release key when done
• VISION will transcribe and execute

💡 TIPS:
• Commands are flexible - try natural variations
• Use Tab to auto-complete
• ESC minimizes to system tray
• App runs in background for instant voice access

🔧 CUSTOMIZATION:
• Click ⚙️ Settings to change voice hotkey
• Default is Ctrl+Windows

📝 EXAMPLES:
✓ "open spotify"
✓ "browse quantum physics youtube"
✓ "search best python libraries"
✓ "open github.com"
✓ "cpu"
✓ "time"
        """.replace("{hotkey}", self.hotkey)
        
        ctk.CTkLabel(
            help_scroll, 
            text=help_text,
            font=("Consolas", 11),
            justify="left",
            anchor="w"
        ).pack(padx=15, pady=10, fill="both")
        
        # Close button
        ctk.CTkButton(
            help_window, 
            text="Got it! 👍", 
            command=help_window.destroy,
            width=150,
            height=40,
            font=("Segoe UI", 13, "bold"),
            fg_color="#00ccff",
            hover_color="#0099cc"
        ).pack(pady=15)

    def setup_ui(self):
        # Header
        self.header = ctk.CTkFrame(self, height=70)
        self.header.pack(fill="x", padx=10, pady=10)
        
        title_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        title_frame.pack(side="left", padx=20)
        ctk.CTkLabel(title_frame, text="👁️ VISION", font=("Segoe UI", 26, "bold"), text_color="#00ccff").pack()
        ctk.CTkLabel(title_frame, text="v2.0 Ultra", font=("Segoe UI", 10), text_color="gray").pack()
        
        self.status_indicator = ctk.CTkLabel(self.header, text="🔴 Loading...", text_color="red", font=("Segoe UI", 12))
        self.status_indicator.pack(side="right", padx=20)
        
        # System stats
        self.stats_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.stats_frame.pack(side="right", padx=10)
        self.cpu_label = ctk.CTkLabel(self.stats_frame, text="CPU: 0%", font=("Consolas", 10), text_color="gray")
        self.cpu_label.pack(side="left", padx=5)
        self.ram_label = ctk.CTkLabel(self.stats_frame, text="RAM: 0%", font=("Consolas", 10), text_color="gray")
        self.ram_label.pack(side="left", padx=5)
        
        # Chat
        self.chat_area = ctk.CTkTextbox(self, font=("Consolas", 13), state="disabled", wrap="word")
        self.chat_area.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Input
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=20, pady=(0, 5))
        
        self.text_input = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Type command or use voice (Ctrl+Win)...", 
            font=("Segoe UI", 14), 
            height=45
        )
        self.text_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.text_input.bind("<Return>", lambda e: self.send_text_command())
        self.text_input.bind("<Up>", lambda e: self.history_up())
        self.text_input.bind("<Down>", lambda e: self.history_down())
        
        self.send_button = ctk.CTkButton(
            self.input_frame, 
            text="⚡ Send", 
            command=self.send_text_command, 
            width=100, 
            height=45, 
            font=("Segoe UI", 14, "bold"),
            fg_color="#00ccff",
            hover_color="#0099cc"
        )
        self.send_button.pack(side="right")
        
        # Presets Section
        presets_frame = ctk.CTkFrame(self)
        presets_frame.pack(fill="x", padx=20, pady=(5, 5))
        
        ctk.CTkLabel(presets_frame, text="⚡ Quick Presets:", font=("Segoe UI", 11, "bold"), text_color="#00ccff").pack(side="left", padx=10)
        
        ctk.CTkButton(
            presets_frame, 
            text="📂 Open", 
            command=lambda: self.use_preset("open"), 
            width=90, 
            height=35,
            font=("Segoe UI", 11),
            fg_color="#1f6aa5",
            hover_color="#144870"
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            presets_frame, 
            text="🔍 Browse", 
            command=lambda: self.use_preset("browse"), 
            width=90, 
            height=35,
            font=("Segoe UI", 11),
            fg_color="#1f6aa5",
            hover_color="#144870"
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            presets_frame, 
            text="🌐 Search", 
            command=lambda: self.use_preset("search"), 
            width=90, 
            height=35,
            font=("Segoe UI", 11),
            fg_color="#1f6aa5",
            hover_color="#144870"
        ).pack(side="left", padx=3)
        
        # Controls
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkButton(control_frame, text="⚙️ Settings", command=self.open_settings, width=100, height=30).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="❓ Help", command=self.show_help, width=100, height=30, fg_color="#9c27b0", hover_color="#7b1fa2").pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="🗑️ Clear", command=self.clear_chat, width=100, height=30).pack(side="left", padx=5)
        ctk.CTkButton(control_frame, text="📋 Copy", command=self.copy_last, width=100, height=30).pack(side="left", padx=5)
        
        self.footer = ctk.CTkLabel(
            self, 
            text=f"⌨️ Type or Hold '{self.hotkey}' | ↑↓ History | ESC to minimize", 
            font=("Segoe UI", 11), 
            text_color="gray"
        )
        self.footer.pack(side="bottom", pady=8)
        
        self.bind("<Escape>", lambda e: self.minimize_to_tray())

    def history_up(self):
        if self.command_history:
            self.history_index = max(0, self.history_index - 1)
            self.text_input.delete(0, 'end')
            self.text_input.insert(0, self.command_history[self.history_index])

    def history_down(self):
        if self.command_history:
            self.history_index = min(len(self.command_history) - 1, self.history_index + 1)
            self.text_input.delete(0, 'end')
            if self.history_index < len(self.command_history):
                self.text_input.insert(0, self.command_history[self.history_index])

    def open_settings(self):
        settings = ctk.CTkToplevel(self)
        settings.title("VISION Settings")
        settings.geometry("400x400")
        settings.transient(self)
        settings.grab_set()
        
        ctk.CTkLabel(settings, text="⚙️ Settings", font=("Segoe UI", 20, "bold")).pack(pady=20)
        
        # Hotkey
        ctk.CTkLabel(settings, text="Voice Hotkey:", font=("Segoe UI", 12)).pack(pady=(10, 5))
        hotkey_var = ctk.StringVar(value=self.hotkey)
        hotkey_entry = ctk.CTkEntry(settings, textvariable=hotkey_var, width=200)
        hotkey_entry.pack(pady=5)
        
        # Startup
        startup_var = ctk.BooleanVar(value=self.config.get("startup", False))
        ctk.CTkCheckBox(settings, text="Run on Startup", variable=startup_var).pack(pady=20)
        
        def save():
            # Save Hotkey
            self.hotkey = hotkey_var.get()
            self.config["hotkey"] = self.hotkey
            
            # Save Startup
            self.config["startup"] = startup_var.get()
            self.set_startup(startup_var.get())
            
            self.save_config()
            self.footer.configure(text=f"⌨️ Type or Hold '{self.hotkey}' | ↑↓ History | ESC to minimize")
            self.add_message("System", f"✓ Settings saved!")
            settings.destroy()
        
        ctk.CTkButton(settings, text="💾 Save", command=save, width=150).pack(pady=20)

    def set_startup(self, enable):
        """Enable or disable run on startup via Registry"""
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "VISION AI"
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Error setting startup: {e}")

    def clear_chat(self):
        self.chat_area.configure(state="normal")
        self.chat_area.delete("1.0", "end")
        self.chat_area.configure(state="disabled")
        self.add_message("System", "Chat cleared")

    def copy_last(self):
        if self.last_response:
            try:
                import pyperclip
                pyperclip.copy(self.last_response)
                self.add_message("System", "✓ Copied")
            except:
                self.add_message("System", "✗ Copy failed")
        else:
            self.add_message("System", "Nothing to copy")

    def update_system_stats(self):
        import time
        while True:
            try:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                self.cpu_label.configure(text=f"CPU: {cpu:.0f}%")
                self.ram_label.configure(text=f"RAM: {ram:.0f}%")
            except:
                pass
            time.sleep(2)

    def create_tray_image(self):
        image = Image.new('RGB', (64, 64), color=(30, 30, 30))
        dc = ImageDraw.Draw(image)
        dc.ellipse((10, 10, 54, 54), fill="#00ccff")
        dc.text((20, 15), "V", fill="white")
        return image

    def minimize_to_tray(self):
        self.withdraw()
        menu = (pystray.MenuItem('Show', self.show_window), pystray.MenuItem('Quit', self.quit_app))
        self.tray_icon = pystray.Icon("VISION", self.create_tray_image(), "VISION AI", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
        self.after(0, self.deiconify)

    def quit_app(self, icon=None, item=None):
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass
            self.browser = None
        if self.tray_icon:
            self.tray_icon.stop()
        self.quit()

    def send_text_command(self):
        text = self.text_input.get().strip()
        if not text:
            return
        
        if not self.command_history or self.command_history[-1] != text:
            self.command_history.append(text)
            if len(self.command_history) > 10:
                self.command_history.pop(0)
        self.history_index = len(self.command_history)
        
        self.text_input.delete(0, 'end')
        self.add_message("You", text)
        threading.Thread(target=self.process_command, args=(text,), daemon=True).start()

    def load_models(self):
        try:
            # Print device profile
            print("\n" + "="*60)
            print("VISION AI - Device Auto-Configuration")
            print("="*60)
            DEVICE_PROFILER.print_profile()
            
            # Optimized Whisper with adaptive threading
            num_threads = PERF_CONFIG['whisper_threads']
            print(f"Loading Whisper ({WHISPER_SIZE}) with {num_threads} threads...")
            
            self.whisper = WhisperModel(
                WHISPER_SIZE, 
                device="cpu", 
                compute_type="int8", 
                num_workers=num_threads
            )
            self.update_status("🟢 Online", "#00ff00")
            self.add_message("VISION", f"⚡ Ready! {WHISPER_SIZE.upper()} model loaded (95% accuracy)")
            self.add_message("VISION", f"💻 Device: {DEVICE_PROFILER.tier.upper()}-END tier")
            self.add_message("VISION", "💡 Tip: Use Quick Presets or click ❓ Help for instructions!")
            winsound.Beep(1000, 150)
        except Exception as e:
            self.update_status("❌ Error", "red")
            self.add_message("Error", str(e))

    def listen_for_hotkey(self):
        while True:
            try:
                if keyboard.is_pressed(self.hotkey):
                    if not self.is_recording:
                        self.start_recording()
                else:
                    if self.is_recording:
                        self.stop_and_process()
                sd.sleep(50)
            except:
                pass

    def start_recording(self):
        self.is_recording = True
        self.audio_data = []
        self.update_status("🎤 Listening...", "#00ccff")
        winsound.Beep(800, 100)
        def callback(indata, frames, time, status):
            if self.is_recording:
                self.audio_data.append(indata.copy())
        self.stream = sd.InputStream(callback=callback, channels=1, samplerate=16000)
        self.stream.start()

    def stop_and_process(self):
        self.is_recording = False
        self.stream.stop()
        self.stream.close()
        self.update_status("⚙️ Processing...", "yellow")
        winsound.Beep(600, 100)
        threading.Thread(target=self.process_audio, daemon=True).start()

    def process_audio(self):
        if not self.audio_data:
            self.update_status("🟢 Online", "#00ff00")
            return
        audio = np.concatenate(self.audio_data, axis=0).flatten().astype(np.float32)
        segments, _ = self.whisper.transcribe(
            audio, 
            beam_size=1, 
            language="en",
            condition_on_previous_text=False  # Better for short commands
        )
        text = " ".join([s.text for s in segments]).strip()
        
        # Clean up common voice recognition issues
        text = self.clean_voice_text(text)
        
        self.audio_data = []
        gc.collect()
        
        if text:
            self.add_message("You", text)
            self.process_command(text)
        else:
            self.update_status("🟢 Online", "#00ff00")

    def clean_voice_text(self, text):
        """Clean up voice recognition artifacts"""
        # Remove punctuation that interferes with commands
        text = text.replace(".", "").replace(",", "").replace("!", "").replace("?", "")
        # Fix common misrecognitions
        text = text.replace(" on YouTube", " youtube").replace(" on YT", " yt")
        text = text.replace(" on Google", "").replace(" on Chrome", "")
        # Remove trailing spaces
        text = " ".join(text.split())
        return text
    
    
    def process_command(self, text):
        """Hybrid routing: Templates → Fast patterns → Simple → LLM (Fallback)"""
        import time
        start_time = time.time()
        
        # PRIORITY 1: Smart template matcher (handles 90% of variations - instant!)
        template_match = self.smart_templates.match(text)
        if template_match:
            success = self.smart_templates.execute(template_match['action'], template_match['params'])
            if success:
                self.update_status("✅ Online", "#00ff00")
                winsound.Beep(1200, 80)
                # Track in memory
                elapsed = time.time() - start_time
                self.memory.remember_command(text, True, elapsed, f"Template: {template_match['action']}")
                return
        
        # PRIORITY 2: Fast complex handler (multi-step - instant!)
        result = self.fast_complex.handle(text)
        if result is True:
            self.update_status("✅ Online", "#00ff00")
            winsound.Beep(1200, 80)
            # Track in memory
            elapsed = time.time() - start_time
            self.memory.remember_command(text, True, elapsed, "Fast complex handler")
            return
        elif result is None:
            return
        
        # PRIORITY 3: Simple pattern matching (instant!)
        if self.instant_execute(text.lower().strip()):
            self.update_status("✅ Online", "#00ff00")
            winsound.Beep(1200, 80)
            # Track in memory
            elapsed = time.time() - start_time
            self.memory.remember_command(text, True, elapsed, "Pattern match")
            return

        # PRIORITY 4: LLM Fallback (for ambiguous/novel commands)
        self.add_message("System", "🤔 Analyzing novel command...")
        
        # Get context (active app, etc)
        context = f"Active App: {self.window_mgr.get_active_window_title()}"
        
        actions = self.llm.parse_ambiguous_command(text, context)
        if actions:
            self.executor.execute_plan(actions)
            self.update_status("✅ Online", "#00ff00")
            # Track in memory
            elapsed = time.time() - start_time
            self.memory.remember_command(text, True, elapsed, f"LLM: {len(actions)} actions", actions)
        else:
            self.add_message("VISION", "🤷 I didn't understand that command.")
            self.update_status("⚠️ Unknown", "orange")
            # Track failure in memory
            elapsed = time.time() - start_time
            self.memory.remember_command(text, False, elapsed, "Not understood")

    def open_windows_settings(self):
        try:
            os.startfile("ms-settings:")
            self.add_message("VISION", "✓ Opened Windows Settings")
        except Exception as e:
            self.add_message("Error", f"Windows Settings failed: {str(e)[:120]}")

    def launch_app(self, app_name):
        """Try to launch desktop or Microsoft Store (UWP) apps by name.
        Returns True on success, False otherwise."""
        name = app_name.strip().lower()

        # Normalize a few common aliases
        alias_map = {
            "zoom workplace": "zoom",
            "zoom meetings": "zoom",
            "windows settings": "settings",
        }
        name = alias_map.get(name, name)

        # 1) Known EXE shortcuts table
        if name in APP_SHORTCUTS:
            try:
                os.startfile(APP_SHORTCUTS[name])
                return True
            except Exception:
                pass

        # 2) Well-known paths (Zoom classic)
        try:
            zoom_path = os.path.expandvars(r"%APPDATA%\Zoom\bin\Zoom.exe")
            if name == "zoom" and os.path.exists(zoom_path):
                os.startfile(zoom_path)
                return True
        except Exception:
            pass

        # 3) Direct EXE by name
        try:
            exe = name if name.endswith(".exe") else f"{name}.exe"
            os.startfile(exe)
            return True
        except Exception:
            pass

        # 4) Microsoft Store (UWP) via AppID lookup
        try:
            ps_cmd = (
                f"$n='{name}'; $a=Get-StartApps | Where-Object {{ $_.Name -like '*'+$n+'*' }} | "
                f"Select-Object -First 1 -ExpandProperty AppID; if($a){{ $a }}"
            )
            res = subprocess.run([
                "powershell", "-NoProfile", "-Command", ps_cmd
            ], capture_output=True, text=True, creationflags=0)
            app_id = (res.stdout or "").strip()
            if app_id:
                subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{app_id}"])
                return True
        except Exception:
            pass

        return False

    def instant_execute(self, text):
        """Ultra-fast pattern matching with agentic context awareness"""
        
        # === AGENTIC CONTEXT-AWARE COMMANDS (Phase 1) ===
        
        # YouTube follow-up commands
        if self.context.youtube_active and self.context.is_context_fresh():
            # Play specific video number
            match = re.search(r'(?:play|click|open|select)\s+(?:the\s+)?(first|second|third|fourth|fifth|1st|2nd|3rd|4th|5th|(\d+)(?:st|nd|rd|th)?)\s*(?:video|one)?', text, re.IGNORECASE)
            if match:
                try:
                    # Map word to number
                    word_to_num = {'first': 1, '1st': 1, 'second': 2, '2nd': 2, 'third': 3, '3rd': 3, 
                                  'fourth': 4, '4th': 4, 'fifth': 5, '5th': 5}
                    num_str = match.group(1) if match.group(1) else match.group(2)
                    video_num = word_to_num.get(num_str.lower(), int(match.group(2))) if match.group(2) else word_to_num.get(num_str.lower(), 1)
                    
                    if 1 <= video_num <= len(self.context.youtube_videos):
                        from selenium.webdriver.common.by import By
                        video_elem = self.context.youtube_videos[video_num - 1]
                        title_elem = video_elem.find_element(By.ID, "video-title")
                        title_elem.click()
                        self.context.youtube_current_index = video_num - 1
                        self.add_message("VISION", f"✓ Playing video #{video_num}")
                        return True
                    else:
                        self.add_message("VISION", f"✗ Video #{video_num} not found (only {len(self.context.youtube_videos)} available)")
                        return True
                except Exception as e:
                    self.add_message("Error", f"Failed to play video: {str(e)[:80]}")
                    return True
            
            # Next/previous video
            if re.search(r'\b(next|skip)\s*(?:video)?\b', text, re.IGNORECASE):
                try:
                    if self.context.youtube_current_index < len(self.context.youtube_videos) - 1:
                        from selenium.webdriver.common.by import By
                        self.context.youtube_current_index += 1
                        video_elem = self.context.youtube_videos[self.context.youtube_current_index]
                        title_elem = video_elem.find_element(By.ID, "video-title")
                        title_elem.click()
                        self.add_message("VISION", f"✓ Next video (#{self.context.youtube_current_index + 1})")
                    else:
                        self.add_message("VISION", "✗ Already at last video")
                    return True
                except Exception as e:
                    self.add_message("Error", f"Failed: {str(e)[:80]}")
                    return True
            
            if re.search(r'\b(previous|back|prior)\s*(?:video)?\b', text, re.IGNORECASE):
                try:
                    if self.context.youtube_current_index > 0:
                        from selenium.webdriver.common.by import By
                        self.context.youtube_current_index -= 1
                        video_elem = self.context.youtube_videos[self.context.youtube_current_index]
                        title_elem = video_elem.find_element(By.ID, "video-title")
                        title_elem.click()
                        self.add_message("VISION", f"✓ Previous video (#{self.context.youtube_current_index + 1})")
                    else:
                        self.add_message("VISION", "✗ Already at first video")
                    return True
                except Exception as e:
                    self.add_message("Error", f"Failed: {str(e)[:80]}")
                    return True
            
            # Video controls (pause/play/stop)
            if re.search(r'\b(pause|stop)\s*(?:video|it)?\b', text, re.IGNORECASE):
                try:
                    # Press 'k' key to pause/play YouTube video
                    self.window_mgr.press_key('k')
                    action = "paused" if "pause" in text else "stopped"
                    self.add_message("VISION", f"✓ Video {action}")
                    return True
                except Exception as e:
                    self.add_message("Error", f"Failed: {str(e)[:80]}")
                    return True
            
            if re.search(r'\b(play|resume|unpause)\b', text, re.IGNORECASE) and 'first' not in text and 'second' not in text and 'third' not in text:
                try:
                    # Press 'k' key to toggle play/pause
                    self.window_mgr.press_key('k')
                    self.add_message("VISION", "✓ Video playing")
                    return True
                except Exception as e:
                    self.add_message("Error", f"Failed: {str(e)[:80]}")
                    return True
            
            # Fullscreen toggle
            if re.search(r'\b(fullscreen|full screen|maximize video)\b', text, re.IGNORECASE):
                try:
                    self.window_mgr.press_key('f')
                    self.add_message("VISION", "✓ Toggled fullscreen")
                    return True
                except Exception as e:
                    self.add_message("Error", f"Failed: {str(e)[:80]}")
                    return True
            
            # Seek forward/backward
            if re.search(r'\b(forward|skip ahead|skip forward)\b', text, re.IGNORECASE):
                try:
                    self.window_mgr.press_key('l')  # 10 seconds forward
                    self.add_message("VISION", "✓ Forward 10s")
                    return True
                except Exception as e:
                    self.add_message("Error", f"Failed: {str(e)[:80]}")
                    return True
            
            if re.search(r'\b(backward|rewind|skip back|go back)\b', text, re.IGNORECASE) and 'video' not in text:
                try:
                    self.window_mgr.press_key('j')  # 10 seconds backward
                    self.add_message("VISION", "✓ Backward 10s")
                    return True
                except Exception as e:
                    self.add_message("Error", f"Failed: {str(e)[:80]}")
                    return True
            
            # Playback speed
            if re.search(r'\b(speed up|faster|increase speed)\b', text, re.IGNORECASE):
                try:
                    self.window_mgr.press_key('>')
                    self.add_message("VISION", "✓ Speed increased")
                    return True
                except Exception as e:
                    self.add_message("Error", f"Failed: {str(e)[:80]}")
                    return True
            
            if re.search(r'\b(slow down|slower|decrease speed|normal speed)\b', text, re.IGNORECASE):
                try:
                    self.window_mgr.press_key('<')
                    self.add_message("VISION", "✓ Speed decreased")
                    return True
                except Exception as e:
                    self.add_message("Error", f"Failed: {str(e)[:80]}")
                    return True
        
        # === WINDOW MANAGEMENT COMMANDS (Phase 3) ===
        
        # Scroll commands
        if re.search(r'\b(scroll|page)\s+(down|up)\b', text, re.IGNORECASE):
            direction = 'down' if 'down' in text else 'up'
            success, msg = self.window_mgr.scroll_page(direction, amount=5)
            self.add_message("VISION" if success else "Error", msg)
            return True
        
        # Volume control
        if re.search(r'\b(?:set\s+)?volume\s+(?:to\s+)?(\d+)', text, re.IGNORECASE):
            match = re.search(r'(\d+)', text)
            if match:
                level = int(match.group(1))
                success, msg = self.window_mgr.set_volume(level)
                self.add_message("VISION" if success else "Error", msg)
                return True
        
        if 'volume up' in text or 'increase volume' in text:
            success, msg = self.window_mgr.volume_up()
            self.add_message("VISION" if success else "Error", msg)
            return True
        
        if 'volume down' in text or 'decrease volume' in text:
            success, msg = self.window_mgr.volume_down()
            self.add_message("VISION" if success else "Error", msg)
            return True
        
        if 'mute' in text or 'unmute' in text:
            success, msg = self.window_mgr.mute_volume()
            self.add_message("VISION" if success else "Error", msg)
            return True
        
        # Screenshot (fix: use word boundary to avoid matching in filenames)
        if re.search(r'\b(take|capture)\s+(a\s+)?screenshot\b', text, re.IGNORECASE) or \
           re.search(r'\bscreenshot\b', text, re.IGNORECASE) and not ('open' in text or 'file' in text):
            success, msg = self.window_mgr.take_screenshot()
            self.add_message("VISION" if success else "Error", msg)
            return True
        
        # Window controls
        if re.search(r'\b(minimize|maximise|maximize|close)\s+(\w+)', text, re.IGNORECASE):
            match = re.search(r'\b(minimize|maximise|maximize|close)\s+(\w+)', text, re.IGNORECASE)
            action = match.group(1).lower()
            window_name = match.group(2)
            
            if 'minim' in action:
                success, msg = self.window_mgr.minimize_window(window_name)
            elif 'maxim' in action:
                success, msg = self.window_mgr.maximize_window(window_name)
            elif 'close' in action:
                success, msg = self.window_mgr.close_window(window_name)
            else:
                return False
            
            self.add_message("VISION" if success else "Error", msg)
            return True
        
        # Snap window
        if 'snap left' in text or 'snap window left' in text:
            success, msg = self.window_mgr.snap_window_left()
            self.add_message("VISION" if success else "Error", msg)
            return True
        
        if 'snap right' in text or 'snap window right' in text:
            success, msg = self.window_mgr.snap_window_right()
            self.add_message("VISION" if success else "Error", msg)
            return True
        
        # Type text (for Notepad or any active window)
        if re.search(r'\b(?:write|type)\s+(.+)', text, re.IGNORECASE):
            match = re.search(r'\b(?:write|type)\s+(.+)', text, re.IGNORECASE)
            text_to_type = match.group(1).strip()
            success, msg = self.window_mgr.type_text(text_to_type)
            self.add_message("VISION" if success else "Error", msg)
            self.context.set_context("notepad")  # Assume notepad is active
            return True
        
        # === FILE MANAGEMENT COMMANDS (Phase 2) ===
        
        # List files (ONLY for simple listing, NOT multi-step tasks)
        # Skip if command has "to X" indicating multi-step (e.g., "list X to Y")
        if re.search(r'\b(?:show|list|display)\s+(?:files?\s+(?:in\s+)?)?(.+?)(?:\s+folder|\s+directory|$)', text, re.IGNORECASE):
            # Check if this is actually a multi-step command
            if not re.search(r'\s+to\s+(google|keep|notepad|docs?|chrome|browser|web)', text, re.IGNORECASE):
                match = re.search(r'\b(?:show|list|display)\s+(?:files?\s+(?:in\s+)?)?(.+?)(?:\s+folder|\s+directory|$)', text, re.IGNORECASE)
                folder = match.group(1).strip() if match.group(1) else None
                
                # Convert common names to actual paths
                folder_map = {
                    'downloads': os.path.expanduser('~/Downloads'),
                    'documents': os.path.expanduser('~/Documents'),
                    'desktop': os.path.expanduser('~/Desktop'),
                    'pictures': os.path.expanduser('~/Pictures'),
                    'videos': os.path.expanduser('~/Videos')
                }
                
                if folder:
                    folder = folder_map.get(folder.lower(), folder)
                
                files = self.file_mgr.list_files(folder)
                if files and 'error' not in files[0]:
                    file_list = "\\n".join([f"{'📁' if f['type'] == 'folder' else '📄'} {f['name']} ({f.get('size', '')})" 
                                           for f in files[:20]])  # Show first 20
                    self.add_message("VISION", f"Files in {self.file_mgr.current_directory}:\\n{file_list}")
                    self.context.set_context("file_explorer", directory=self.file_mgr.current_directory, files=files)
                else:
                    self.add_message("Error", files[0].get('error', 'Unknown error') if files else "No files found")
                return True
        
        # Search files
        if re.search(r'\b(?:find|search|locate)\s+(?:file\s+)?(.+)', text, re.IGNORECASE):
            # Don't conflict with web search OR multi-step commands
            if 'google' not in text and 'web' not in text and not text.startswith('search ') and \
               not re.search(r'\s+to\s+', text, re.IGNORECASE):
                match = re.search(r'\b(?:find|search|locate)\s+(?:file\s+)?(.+)', text, re.IGNORECASE)
                pattern = match.group(1).strip()
                results = self.file_mgr.search_files(pattern)
                
                if results and 'error' not in results[0]:
                    result_list = "\\n".join([f"📄 {r['name']} - {r['path']}" for r in results[:10]])
                    self.add_message("VISION", f"Found {len(results)} files:\\n{result_list}")
                else:
                    self.add_message("Error", results[0].get('error', 'No files found') if results else "No files found")
                return True
        
        # === EXISTING COMMANDS (Keep all original functionality) ===
        
        # System commands
        if "clear" in text:
            self.clear_chat()
            return True
        
        # Open VISION settings only if user explicitly asks for app settings (not Windows settings)
        if (re.fullmatch(r"(?:open\s+)?settings", text) or re.search(r"\bconfig\b", text)) and "windows" not in text:
            self.open_settings()
            return True

        # Windows Settings (ms-settings:)
        if re.search(r"\bopen\s+windows\s+settings\b", text) or re.fullmatch(r"windows\s+settings", text):
            self.open_windows_settings()
            return True
        
        if "copy" in text:
            self.copy_last()
            return True
        
        # YouTube browse/search with automation
        # Pattern 1: "browse/search/play XYZ youtube" or "browse/search/play XYZ on youtube"
        yt_match = re.search(r"(?:browse|search|play|find|open)\s+(.+?)\s+(?:on\s+)?(?:youtube|yt)(?:\s|$)", text, re.IGNORECASE)
        if yt_match:
            query = yt_match.group(1).strip()
            self.automate_youtube(query)
            return True
        
        # Pattern 2: "XYZ youtube" or "XYZ on youtube" (without command verb)
        if "youtube" in text or " yt" in text:
            # Extract everything before youtube/yt as query
            yt_split = re.split(r'\s+(?:on\s+)?(?:youtube|yt)(?:\s|$)', text, flags=re.IGNORECASE)
            if len(yt_split) > 1 and yt_split[0].strip():
                query = yt_split[0].strip()
                # Remove common command words from start
                query = re.sub(r'^(?:browse|search|play|find|open)\s+', '', query, flags=re.IGNORECASE)
                if query:  # Only proceed if there's a query left
                    self.automate_youtube(query)
                    return True
        
        # General search
        m = re.search(r"(?:search|google|find)\s+(?:for\s+)?(.+)", text)
        if m:
            q = m.group(1).strip()
            os.startfile(f"https://www.google.com/search?q={q.replace(' ', '+')}")
            self.add_message("VISION", f"✓ Searching: {q}")
            return True
        
        # URL shortcuts (only when not an explicit "open/start" app command)
        if not re.match(r"(open|launch|start|run)\s+", text):
            for key, url in URL_SHORTCUTS.items():
                if key in text.split():
                    os.startfile(f"https://{url}")
                    self.add_message("VISION", f"✓ Opened {key}")
                    return True
        
        # Open command with potential query OR file/folder path
        m = re.search(r"(?:open|launch|start|run)\s+(.+)", text)
        if m:
            full_target = m.group(1).strip()
            
            # CHECK IF IT'S A FILE OR FOLDER PATH FIRST
            # Patterns: C:\..., D:\..., ./..., file.ext, "path with spaces"
            if os.path.exists(full_target):
                # It's a valid file or folder - open it
                try:
                    os.startfile(full_target)
                    self.add_message("VISION", f"✓ Opened {full_target}")
                    return True
                except Exception as e:
                    self.add_message("Error", f"Failed to open: {str(e)[:80]}")
                    return True
            
            # Also try expanding user paths like ~/Downloads/file.txt and %USERPROFILE%\Documents
            expanded_path = os.path.expandvars(os.path.expanduser(full_target))
            if os.path.exists(expanded_path):
                try:
                    os.startfile(expanded_path)
                    self.add_message("VISION", f"✓ Opened {expanded_path}")
                    return True
                except Exception as e:
                    self.add_message("Error", f"Failed to open: {str(e)[:80]}")
                    return True
            
            # Not a file/folder, proceed with app/url logic
            full_target_lower = full_target.lower()
            
            # Check if there's a query after the app/url (e.g., "open youtube dhruv rathee")
            parts = full_target_lower.split(None, 1)  # Split into first word and rest
            app = parts[0]
            query = parts[1] if len(parts) > 1 else None

            # Special case: Windows settings
            if app == "windows" and query and query.startswith("settings"):
                self.open_windows_settings()
                return True

            # First, try to launch as a local app (Desktop/UWP)
            if self.launch_app(app):
                self.add_message("VISION", f"✓ Opened {app}")
                return True
            
            # Try full target as URL
            if "." in full_target:
                url = f"https://{full_target}" if not full_target.startswith("http") else full_target
                os.startfile(url)
                self.add_message("VISION", f"✓ Opened {full_target}")
                return True
            
            # If still not found, fall back to URL shortcuts (e.g., open whatsapp => web if app missing)
            if app in URL_SHORTCUTS:
                os.startfile(f"https://{URL_SHORTCUTS[app]}")
                self.add_message("VISION", f"✓ Opened {app} (web)")
                return True

            # Final fallback: report not found
            self.add_message("VISION", f"✗ Can't find {app}")
            return True
        
        # System info
        if "cpu" in text or "processor" in text:
            cpu = psutil.cpu_percent(interval=0.5)
            self.add_message("VISION", f"CPU: {cpu}%")
            return True
        
        if "ram" in text or "memory" in text:
            ram = psutil.virtual_memory()
            self.add_message("VISION", f"RAM: {ram.percent}% ({ram.used//(1024**3)}GB / {ram.total//(1024**3)}GB)")
            return True
        
        # Time
        if "time" in text:
            self.add_message("VISION", datetime.now().strftime("Time: %I:%M %p"))
            return True
        
        if "date" in text:
            self.add_message("VISION", datetime.now().strftime("Date: %B %d, %Y"))
            return True
        
        # Automation
        if "automate" in text and "youtube" in text:
            m = re.search(r"(?:search|play|find)\s+(.+?)(?:\s+on|$)", text)
            if m:
                self.automate_youtube(m.group(1).strip())
                return True
        
        return False

    def automate_youtube(self, query, auto_play_first=False):
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
            import time
            
            # FIXED: Close existing browser to prevent memory leak
            if self.browser:
                try:
                    self.browser.quit()
                except:
                    pass
                finally:
                    self.browser = None
            
            # Create new browser
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            opts = Options()
            opts.add_argument("--start-maximized")
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
            opts.add_experimental_option("useAutomationExtension", False)
            self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
            
            self.browser.get("https://www.youtube.com")
            time.sleep(1.5)
            search = self.browser.find_element(By.NAME, "search_query")
            search.clear()
            search.send_keys(query)
            search.send_keys(Keys.RETURN)
            time.sleep(2)  # Wait for results to load
            
            # Find all video elements
            try:
                videos = self.browser.find_elements(By.CSS_SELECTOR, "ytd-video-renderer")
                if videos:
                    # Set YouTube context
                    self.context.set_context("youtube", browser=self.browser, videos=videos)
                    self.context.add_command(f"browse {query} youtube", "YouTube search completed", "youtube")
                    
                    msg = f"✓ YouTube: {query} ({len(videos)} videos)"
                    if auto_play_first and len(videos) > 0:
                        # Auto-click first video
                        try:
                            first_video = videos[0].find_element(By.ID, "video-title")
                            first_video.click()
                            self.context.youtube_current_index = 0
                            msg += " - Playing first video"
                        except:
                            pass
                    
                    self.add_message("VISION", msg)
                else:
                    self.add_message("VISION", f"✓ YouTube: {query} (no results)")
            except Exception as e:
                self.add_message("VISION", f"✓ YouTube: {query}")
                
        except Exception as e:
            self.browser = None  # Reset browser on error
            self.add_message("Error", f"YouTube failed: {str(e)[:100]}")


    def add_message(self, sender, text):
        def _update_ui():
            t = datetime.now().strftime("%H:%M")
            self.chat_area.configure(state="normal")
            if sender == "VISION":
                self.last_response = text
                self.chat_area.insert("end", f"[{t}] 👁️ {text}\n\n")
            elif sender == "System":
                self.chat_area.insert("end", f"[{t}] 🔧 {text}\n\n")
            elif sender == "Error":
                self.chat_area.insert("end", f"[{t}] ⚠️ {text}\n\n")
            else:
                self.chat_area.insert("end", f"[{t}] 👤 {text}\n\n")
            self.chat_area.configure(state="disabled")
            self.chat_area.see("end")
            
        # Schedule update on main thread
        self.after(0, _update_ui)

    def update_status(self, text, color):
        self.after(0, lambda: self.status_indicator.configure(text=text, text_color=color))

if __name__ == "__main__":
    try:
        import pyperclip
    except:
        pass
    app = VisionAI()
    app.mainloop()
