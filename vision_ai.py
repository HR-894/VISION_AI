import customtkinter as ctk
import sys, os, threading, json, keyboard, re, subprocess
import sounddevice as sd
import numpy as np
import winsound, psutil, gc
from faster_whisper import WhisperModel
import pystray
from PIL import Image, ImageDraw
from datetime import datetime

# --- Config ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WHISPER_SIZE = "base"  # Options: tiny, base, small, medium, large-v3 (tiny=fastest, large=most accurate)
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

        self.title("VISION AI v2.0 Ultra")
        self.geometry("900x700")
        ctk.set_appearance_mode("Dark")
        
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.tray_icon = None
        self.browser = None
        self.command_history = []
        self.history_index = -1
        self.last_response = ""

        self.setup_ui()
        
        self.is_recording = False
        self.audio_data = []
        
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
        
        # Controls
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkButton(control_frame, text="⚙️ Settings", command=self.open_settings, width=100, height=30).pack(side="left", padx=5)
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
        settings.geometry("400x300")
        settings.transient(self)
        settings.grab_set()
        
        ctk.CTkLabel(settings, text="⚙️ Settings", font=("Segoe UI", 20, "bold")).pack(pady=20)
        ctk.CTkLabel(settings, text="Voice Hotkey:", font=("Segoe UI", 12)).pack(pady=(10, 5))
        hotkey_var = ctk.StringVar(value=self.hotkey)
        hotkey_entry = ctk.CTkEntry(settings, textvariable=hotkey_var, width=200)
        hotkey_entry.pack(pady=5)
        
        def save():
            self.hotkey = hotkey_var.get()
            self.config["hotkey"] = self.hotkey
            self.save_config()
            self.footer.configure(text=f"⌨️ Type or Hold '{self.hotkey}' | ↑↓ History | ESC to minimize")
            self.add_message("System", f"✓ Hotkey: {self.hotkey}")
            settings.destroy()
        
        ctk.CTkButton(settings, text="💾 Save", command=save, width=150).pack(pady=20)

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
            # Optimized Whisper with no punctuation for cleaner voice commands
            self.whisper = WhisperModel(
                WHISPER_SIZE, 
                device="cpu", 
                compute_type="int8", 
                num_workers=4
            )
            self.update_status("🟢 Online", "#00ff00")
            self.add_message("VISION", "⚡ Ready! Lightning mode (No LLM - 100% Pattern Matching)")
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
        if self.instant_execute(text.lower().strip()):
            self.update_status("🟢 Online", "#00ff00")
            winsound.Beep(1200, 80)

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
        """Ultra-fast pattern matching"""
        
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
        
        # Open command with potential query
        m = re.search(r"(?:open|launch|start|run)\s+(.+)", text)
        if m:
            full_target = m.group(1).strip().lower()
            
            # Check if there's a query after the app/url (e.g., "open youtube dhruv rathee")
            parts = full_target.split(None, 1)  # Split into first word and rest
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

    def automate_youtube(self, query):
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
            import time
            
            # Check if browser exists and is valid
            browser_valid = False
            if self.browser:
                try:
                    # Test if browser is still alive
                    self.browser.current_url
                    browser_valid = True
                except (InvalidSessionIdException, WebDriverException):
                    self.browser = None
            
            # Create new browser if needed
            if not browser_valid:
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
            self.add_message("VISION", f"✓ YouTube: {query}")
        except Exception as e:
            self.browser = None  # Reset browser on error
            self.add_message("Error", f"YouTube failed: {str(e)[:100]}")

    def add_message(self, sender, text):
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

    def update_status(self, text, color):
        self.status_indicator.configure(text=text, text_color=color)

if __name__ == "__main__":
    try:
        import pyperclip
    except:
        pass
    app = VisionAI()
    app.mainloop()
