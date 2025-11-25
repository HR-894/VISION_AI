"""
Window Manager for VISION AI
Controls windows, desktop, and system settings
"""

import os
import pyautogui
import win32gui
import win32con
import win32api
import win32process
import psutil
from typing import List, Dict, Optional, Tuple
from PIL import ImageGrab
from datetime import datetime

class WindowManager:
    """Manages windows and system controls"""
    
    def __init__(self):
        self.window_cache = {}
        pyautogui.PAUSE = 0.5  # Slight pause between actions
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    
    def find_window(self, title_pattern: str) -> Optional[int]:
        """Find window by title pattern"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if title_pattern.lower() in window_title.lower():
                    windows.append((hwnd, window_title))
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        if windows:
            # Cache the result
            self.window_cache[title_pattern] = windows[0][0]
            return windows[0][0]
        return None
    
    def list_windows(self) -> List[Dict[str, str]]:
        """List all visible windows"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:  # Only windows with titles
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        windows.append({
                            'hwnd': hwnd,
                            'title': title,
                            'process': process.name()
                        })
                    except:
                        windows.append({
                            'hwnd': hwnd,
                            'title': title,
                            'process': 'unknown'
                        })
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows
    
    def minimize_window(self, title_pattern: str) -> Tuple[bool, str]:
        """Minimize window by title"""
        hwnd = self.find_window(title_pattern)
        if hwnd:
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                return True, f"✓ Minimized: {title_pattern}"
            except Exception as e:
                return False, f"✗ Failed to minimize: {str(e)}"
        return False, f"✗ Window not found: {title_pattern}"
    
    def maximize_window(self, title_pattern: str) -> Tuple[bool, str]:
        """Maximize window by title"""
        hwnd = self.find_window(title_pattern)
        if hwnd:
            try:
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                return True, f"✓ Maximized: {title_pattern}"
            except Exception as e:
                return False, f"✗ Failed to maximize: {str(e)}"
        return False, f"✗ Window not found: {title_pattern}"
    
    def close_window(self, title_pattern: str) -> Tuple[bool, str]:
        """Close window by title"""
        hwnd = self.find_window(title_pattern)
        if hwnd:
            try:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                return True, f"✓ Closed: {title_pattern}"
            except Exception as e:
                return False, f"✗ Failed to close: {str(e)}"
        return False, f"✗ Window not found: {title_pattern}"
    
    def focus_window(self, title_pattern: str) -> Tuple[bool, str]:
        """Bring window to front"""
        hwnd = self.find_window(title_pattern)
        if hwnd:
            try:
                win32gui.SetForegroundWindow(hwnd)
                return True, f"✓ Focused: {title_pattern}"
            except Exception as e:
                return False, f"✗ Failed to focus: {str(e)}"
        return False, f"✗ Window not found: {title_pattern}"
    
    def snap_window_left(self) -> Tuple[bool, str]:
        """Snap active window to left half"""
        try:
            pyautogui.hotkey('win', 'left')
            return True, "✓ Snapped window left"
        except Exception as e:
            return False, f"✗ Failed to snap: {str(e)}"
    
    def snap_window_right(self) -> Tuple[bool, str]:
        """Snap active window to right half"""
        try:
            pyautogui.hotkey('win', 'right')
            return True, "✓ Snapped window right"
        except Exception as e:
            return False, f"✗ Failed to snap: {str(e)}"
    
    def take_screenshot(self, save_path: Optional[str] = None) -> Tuple[bool, str]:
        """Take screenshot of entire screen"""
        try:
            # Generate filename if not provided
            if not save_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
                save_path = os.path.join(downloads, f'screenshot_{timestamp}.png')
            
            # Capture screenshot
            screenshot = ImageGrab.grab()
            screenshot.save(save_path)
            
            return True, f"✓ Screenshot saved: {save_path}"
        except Exception as e:
            return False, f"✗ Screenshot failed: {str(e)}"
    
    def set_volume(self, level: int) -> Tuple[bool, str]:
        """Set system volume (0-100)"""
        try:
            if not 0 <= level <= 100:
                return False, "✗ Volume must be between 0 and 100"
            
            # Calculate key presses needed
            # Volume down to 0, then up to desired level
            for _ in range(50):  # Max down
                pyautogui.press('volumedown')
            
            steps = int(level / 2)  # Each press is ~2%
            for _ in range(steps):
                pyautogui.press('volumeup')
            
            return True, f"✓ Volume set to ~{level}%"
        except Exception as e:
            return False, f"✗ Failed to set volume: {str(e)}"
    
    def volume_up(self) -> Tuple[bool, str]:
        """Increase volume"""
        try:
            pyautogui.press('volumeup')
            return True, "✓ Volume up"
        except Exception as e:
            return False, f"✗ Failed: {str(e)}"
    
    def volume_down(self) -> Tuple[bool, str]:
        """Decrease volume"""
        try:
            pyautogui.press('volumedown')
            return True, "✓ Volume down"
        except Exception as e:
            return False, f"✗ Failed: {str(e)}"
    
    def mute_volume(self) -> Tuple[bool, str]:
        """Mute/unmute volume"""
        try:
            pyautogui.press('volumemute')
            return True, "✓ Volume muted/unmuted"
        except Exception as e:
            return False, f"✗ Failed: {str(e)}"
    
    def scroll_page(self, direction: str, amount: int = 3) -> Tuple[bool, str]:
        """Scroll current window"""
        try:
            if direction.lower() in ['down', 'up']:
                scroll_amount = -amount if direction.lower() == 'down' else amount
                pyautogui.scroll(scroll_amount * 100)  # Multiply for visible effect
                return True, f"✓ Scrolled {direction}"
            else:
                return False, "✗ Direction must be 'up' or 'down'"
        except Exception as e:
            return False, f"✗ Scroll failed: {str(e)}"
    
    def press_key(self, key: str) -> Tuple[bool, str]:
        """Press a keyboard key"""
        try:
            pyautogui.press(key.lower())
            return True, f"✓ Pressed: {key}"
        except Exception as e:
            return False, f"✗ Failed to press key: {str(e)}"
    
    def type_text(self, text: str, interval: float = 0.05) -> Tuple[bool, str]:
        """Type text with specified interval between characters"""
        try:
            pyautogui.write(text, interval=interval)
            return True, f"✓ Typed: {text[:50]}{'...' if len(text) > 50 else ''}"
        except Exception as e:
            return False, f"✗ Failed to type: {str(e)}"
    
    def show_desktop(self) -> Tuple[bool, str]:
        """Show/minimize all windows (show desktop)"""
        try:
            pyautogui.hotkey('win', 'd')
            return True, "✓ Showed desktop"
        except Exception as e:
            return False, f"✗ Failed: {str(e)}"
