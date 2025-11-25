"""
Context Manager for VISION AI
Tracks application state and context for agentic follow-up commands
"""

import time
from typing import Optional, List, Dict, Any

class ContextManager:
    """Manages application context and state tracking"""
    
    def __init__(self):
        # Current active context
        self.current_app: Optional[str] = None  # "youtube", "notepad", "browser", "file_explorer", None
        self.last_command: Optional[str] = None
        self.last_command_time: float = 0
        
        # YouTube context
        self.youtube_active = False
        self.youtube_videos: List[Any] = []  # Selenium WebElements
        self.youtube_current_index = -1
        
        # Notepad context
        self.notepad_active = False
        self.notepad_handle = None
        self.notepad_process = None
        
        # Browser context (general web)
        self.browser_active = False
        self.browser = None
        self.browser_current_url = None
        
        # File explorer context
        self.file_explorer_active = False
        self.current_directory = None
        self.current_files: List[str] = []
        
        # Command history
        self.command_history: List[Dict[str, Any]] = []
        self.max_history = 10
        
    def set_context(self, app: str, **kwargs):
        """Set the current application context"""
        self.current_app = app
        
        if app == "youtube":
            self.youtube_active = True
            self.browser_active = False
            if 'videos' in kwargs:
                self.youtube_videos = kwargs['videos']
            if 'browser' in kwargs:
                self.browser = kwargs['browser']
                
        elif app == "notepad":
            self.notepad_active = True
            if 'handle' in kwargs:
                self.notepad_handle = kwargs['handle']
            if 'process' in kwargs:
                self.notepad_process = kwargs['process']
                
        elif app == "browser":
            self.browser_active = True
            self.youtube_active = False
            if 'browser' in kwargs:
                self.browser = kwargs['browser']
            if 'url' in kwargs:
                self.browser_current_url = kwargs['url']
                
        elif app == "file_explorer":
            self.file_explorer_active = True
            if 'directory' in kwargs:
                self.current_directory = kwargs['directory']
            if 'files' in kwargs:
                self.current_files = kwargs['files']
    
    def clear_context(self, app: Optional[str] = None):
        """Clear context for specific app or all"""
        if app is None or app == "youtube":
            self.youtube_active = False
            self.youtube_videos = []
            self.youtube_current_index = -1
            
        if app is None or app == "notepad":
            self.notepad_active = False
            self.notepad_handle = None
            self.notepad_process = None
            
        if app is None or app == "browser":
            self.browser_active = False
            self.browser_current_url = None
            
        if app is None or app == "file_explorer":
            self.file_explorer_active = False
            self.current_directory = None
            self.current_files = []
            
        if app is None:
            self.current_app = None
            self.browser = None
    
    def add_command(self, command: str, result: str, context: Optional[str] = None):
        """Add command to history"""
        self.command_history.append({
            'command': command,
            'result': result,
            'context': context or self.current_app,
            'timestamp': time.time()
        })
        
        # Keep only last N commands
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
        
        self.last_command = command
        self.last_command_time = time.time()
    
    def get_context_info(self) -> str:
        """Get readable context information"""
        if self.youtube_active:
            return f"YouTube active ({len(self.youtube_videos)} videos loaded)"
        elif self.notepad_active:
            return "Notepad active"
        elif self.browser_active:
            return f"Browser active: {self.browser_current_url or 'unknown URL'}"
        elif self.file_explorer_active:
            return f"File Explorer: {self.current_directory or 'unknown location'}"
        else:
            return "No active context"
    
    def is_context_fresh(self, max_age_seconds: int = 300) -> bool:
        """Check if current context is still fresh (default 5 minutes)"""
        if self.last_command_time == 0:
            return False
        return (time.time() - self.last_command_time) < max_age_seconds
    
    def get_last_commands(self, n: int = 5) -> List[str]:
        """Get last N commands"""
        return [cmd['command'] for cmd in self.command_history[-n:]]
