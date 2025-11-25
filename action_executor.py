"""
Multi-Step Action Executor for VISION AI
Executes action plans from LLM sequentially
"""

import time
from typing import List, Dict, Any, Tuple, Optional

class ActionExecutor:
    """Executes multi-step action plans"""
    
    def __init__(self, vision_ai_instance):
        """
        Initialize with VisionAI instance to access all methods
        Args:
            vision_ai_instance: The main VisionAI class instance
        """
        self.vision = vision_ai_instance
        
        # Map action names to methods
        self.action_map = {
            "list_files": self._list_files,
            "open_app": self._open_app,
            "open_file": self._open_file,  # NEW
            "type_text": self._type_text,
            "press_key": self._press_key,  # NEW
            "search_files": self._search_files,
            "search_web": self._search_web,  # NEW
            "create_folder": self._create_folder,
            "move_file": self._move_file,
            "copy_file": self._copy_file,
            "screenshot": self._screenshot,
            "open_browser": self._open_browser,
            "wait": self._wait,
            "focus_window": self._focus_window,
            "click_element": self._click_element,
            "scroll": self._scroll
        }
    
    def execute_plan(self, actions: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Execute a list of actions sequentially
        Returns: (success: bool, results: List[str])
        """
        results = []
        
        self.vision.add_message("VISION", f"📋 Executing {len(actions)} steps...")
        
        for i, action in enumerate(actions, 1):
            action_name = action.get("action")
            params = action.get("params", {})
            
            if action_name not in self.action_map:
                error_msg = f"❌ Step {i}/{len(actions)}: Unknown action '{action_name}'"
                results.append(error_msg)
                self.vision.add_message("Error", error_msg)
                continue
            
            try:
                # Execute action
                self.vision.add_message("System", f"⚙️ Step {i}/{len(actions)}: {action_name}...")
                success, message = self.action_map[action_name](**params)
                
                if success:
                    results.append(f"✓ Step {i}: {message}")
                    self.vision.add_message("VISION", message)
                else:
                    results.append(f"✗ Step {i}: {message}")
                    self.vision.add_message("Error", message)
                    # Continue even if one step fails (best effort)
                
                # Small delay between actions
                time.sleep(0.3)
            
            except Exception as e:
                error_msg = f"✗ Step {i}: {str(e)[:100]}"
                results.append(error_msg)
                self.vision.add_message("Error", error_msg)
        
        success = all("✓" in r for r in results)
        self.vision.add_message("VISION", f"{'✓ All steps completed!' if success else '⚠️ Completed with errors'}")
        
        return success, results
    
    # === ACTION IMPLEMENTATIONS ===
    
    def _open_file(self, path: str) -> Tuple[bool, str]:
        """Open a file or folder"""
        try:
            import os
            # Expand ~ to home directory
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                os.startfile(expanded_path)
                return True, f"✓ Opened {path}"
            else:
                return False, f"File not found: {path}"
        except Exception as e:
            return False, f"Failed to open: {str(e)[:60]}"
    
    def _press_key(self, key: str) -> Tuple[bool, str]:
        """Press a keyboard key"""
        try:
            self.vision.window_mgr.press_key(key)
            return True, f"✓ Pressed {key}"
        except Exception as e:
            return False, f"Failed to press key: {str(e)[:60]}"
    
    def _search_web(self, query: str, engine: str = "google") -> Tuple[bool, str]:
        """Search the web"""
        try:
            import os
            if engine == "youtube":
                url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            else:  # Default to Google
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            os.startfile(url)
            return True, f"✓ Searching: {query}"
        except Exception as e:
            return False, f"Search failed: {str(e)[:60]}"
    
    def _list_files(self, directory: str = None) -> Tuple[bool, str]:
        """List files in directory"""
        try:
            files = self.vision.file_mgr.list_files(directory)
            if files and 'error' not in files[0]:
                return True, f"✓ Listed {len(files)} items in {self.vision.file_mgr.current_directory}"
            else:
                return False, files[0].get('error', 'Failed to list files') if files else "No files found"
        except Exception as e:
            return False, f"Failed: {str(e)[:80]}"
    
    def _open_app(self, app_name: str) -> Tuple[bool, str]:
        """Open an application"""
        try:
            # Use existing launch_app method
            success = self.vision.launch_app(app_name)
            if success:
                return True, f"✓ Opened {app_name}"
            else:
                # Try via os.startfile
                import os
                os.startfile(app_name)
                return True, f"✓ Opened {app_name}"
        except Exception as e:
            return False, f"Failed to open {app_name}: {str(e)[:60]}"
    
    def _type_text(self, text: str) -> Tuple[bool, str]:
        """Type text in active window"""
        return self.vision.window_mgr.type_text(text)
    
    def _search_files(self, pattern: str, directory: str = None) -> Tuple[bool, str]:
        """Search for files"""
        try:
            results = self.vision.file_mgr.search_files(pattern, directory)
            if results and 'error' not in results[0]:
                return True, f"✓ Found {len(results)} files matching '{pattern}'"
            else:
                return False, "No files found"
        except Exception as e:
            return False, f"Search failed: {str(e)[:80]}"
    
    def _create_folder(self, path: str) -> Tuple[bool, str]:
        """Create a new folder"""
        try:
            import os
            os.makedirs(path, exist_ok=True)
            return True, f"✓ Created folder: {path}"
        except Exception as e:
            return False, f"Failed to create folder: {str(e)[:60]}"
    
    def _move_file(self, source: str, destination: str) -> Tuple[bool, str]:
        """Move a file"""
        return self.vision.file_mgr.move_file(source, destination)
    
    def _copy_file(self, source: str, destination: str) -> Tuple[bool, str]:
        """Copy a file"""
        return self.vision.file_mgr.copy_file(source, destination)
    
    def _screenshot(self) -> Tuple[bool, str]:
        """Take a screenshot"""
        return self.vision.window_mgr.take_screenshot()
    
    def _open_browser(self, url: str) -> Tuple[bool, str]:
        """Open browser with URL"""
        try:
            import os
            if not url.startswith('http'):
                url = f'https://{url}'
            os.startfile(url)
            return True, f"✓ Opened {url}"
        except Exception as e:
            return False, f"Failed: {str(e)[:60]}"
    
    def _wait(self, seconds: float = 1.0) -> Tuple[bool, str]:
        """Wait for specified seconds"""
        time.sleep(seconds)
        return True, f"✓ Waited {seconds}s"
    
    def _focus_window(self, window_name: str) -> Tuple[bool, str]:
        """Focus a window"""
        return self.vision.window_mgr.focus_window(window_name)
    
    def _click_element(self, element: str) -> Tuple[bool, str]:
        """Click screen element (placeholder - would need OCR/CV)"""
        return False, "Click element not yet implemented"
    
    def _scroll(self, direction: str = "down", amount: int = 3) -> Tuple[bool, str]:
        """Scroll window"""
        return self.vision.window_mgr.scroll_page(direction, amount)
