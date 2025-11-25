"""
Safety Guard for VISION AI
Protects system files and enforces safety confirmations
"""

import os
import re
from typing import List, Tuple, Optional

class SafetyGuard:
    """Enforces safety rules and confirmations"""
    
    # Protected paths - NEVER allow operations here
    PROTECTED_PATHS = [
        r"C:\\Windows",
        r"C:\\Program Files",
        r"C:\\Program Files (x86)",
        r"C:\\ProgramData\\Microsoft",
        r"C:\\System32",
        r"C:\\$",  # System volume information
    ]
    
    # Actions requiring single confirmation
    CAUTION_ACTIONS = [
        'move', 'rename', 'copy', 'edit', 'modify', 'change'
    ]
    
    # Actions requiring double confirmation
    DANGER_ACTIONS = [
        'delete', 'remove', 'format', 'wipe', 'erase',
        'restart', 'shutdown', 'reboot', 'reset'
    ]
    
    def __init__(self):
        # Add user profile protected paths
        user_profile = os.environ.get('USERPROFILE', '')
        if user_profile:
            self.PROTECTED_PATHS.extend([
                os.path.join(user_profile, 'AppData', 'Roaming', 'Microsoft'),
                os.path.join(user_profile, 'AppData', 'Local', 'Microsoft'),
            ])
        
        self.action_log = []
    
    def is_path_protected(self, path: str) -> Tuple[bool, Optional[str]]:
        """Check if path is in protected zone"""
        if not path:
            return False, None
        
        # Resolve to absolute path
        try:
            abs_path = os.path.abspath(path)
        except:
            abs_path = path
        
        # Check against protected paths
        for protected in self.PROTECTED_PATHS:
            protected_abs = os.path.abspath(protected)
            if abs_path.startswith(protected_abs):
                return True, protected
        
        return False, None
    
    def get_action_level(self, command: str) -> str:
        """Determine safety level of action: SAFE, CAUTION, DANGER"""
        command_lower = command.lower()
        
        # Check for dangerous actions
        for action in self.DANGER_ACTIONS:
            if action in command_lower:
                return 'DANGER'
        
        # Check for caution actions
        for action in self.CAUTION_ACTIONS:
            if action in command_lower:
                return 'CAUTION'
        
        return 'SAFE'
    
    def validate_file_operation(self, operation: str, path: str) -> Tuple[bool, str]:
        """
        Validate file operation safety
        Returns: (allowed: bool, reason: str)
        """
        # Check if path is protected
        is_protected, protected_path = self.is_path_protected(path)
        if is_protected:
            return False, f"🚫 BLOCKED: Cannot {operation} in protected system directory: {protected_path}"
        
        # Check if trying to access C:\\ root system folders
        if path.lower().startswith('c:\\') and len(path.split('\\')) <= 2:
            common_system = ['windows', 'program files', 'program files (x86)', 'programdata']
            for sys_dir in common_system:
                if sys_dir in path.lower():
                    return False, f"🚫 BLOCKED: Cannot {operation} system directory: {path}"
        
        return True, "✓ Safe to proceed"
    
    def requires_confirmation(self, command: str) -> Tuple[str, int]:
        """
        Check if command requires confirmation
        Returns: (level, confirmation_count)
        level: SAFE (0), CAUTION (1), DANGER (2)
        """
        level = self.get_action_level(command)
        
        if level == 'DANGER':
            return 'DANGER', 2
        elif level == 'CAUTION':
            return 'CAUTION', 1
        else:
            return 'SAFE', 0
    
    def log_action(self, action: str, target: str, status: str):
        """Log action to history"""
        import datetime
        log_entry = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': action,
            'target': target,
            'status': status
        }
        self.action_log.append(log_entry)
        
        # Also write to file
        try:
            log_file = os.path.join(os.path.dirname(__file__), 'vision_actions.log')
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{log_entry['timestamp']}] {status}: {action} - {target}\n")
        except:
            pass
    
    def get_safe_delete_message(self, path: str) -> str:
        """Get user-friendly delete confirmation message"""
        filename = os.path.basename(path)
        return f"⚠️ Delete '{filename}'? (Will go to Recycle Bin)"
    
    def get_danger_confirmation_message(self, action: str, target: str) -> List[str]:
        """Get double confirmation messages for dangerous actions"""
        return [
            f"⚠️ WARNING: About to {action} '{target}'. Are you sure? (yes/no)",
            f"🚨 FINAL CONFIRMATION: Really {action} '{target}'? Type 'YES' to confirm:"
        ]
