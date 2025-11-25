"""
Smart Template Matcher - Handles 90% of commands instantly
No LLM needed - Pure template matching with variable extraction
"""

import re
from typing import Optional, Dict, List, Tuple

class SmartTemplateMatcher:
    """Matches commands to templates and extracts variables"""
    
    def __init__(self, vision_ai):
        self.vision = vision_ai
        
        # Define command templates with variable slots
        self.templates = [
            # File operations
            {
                'pattern': r'(?:list|show|display|get)\s+(?:all\s+)?(?:files?\s+)?(?:in\s+)?(.+?)(?:\s+folder|\s+directory|$)',
                'action': 'list_files',
                'extract': ['location']
            },
            {
                'pattern': r'(?:find|search|locate)\s+(?:all\s+)?(.+?)\s+(?:files?|in)\s+(.+)',
                'action': 'search_files',
                'extract': ['file_type', 'location']
            },
            {
                'pattern': r'(?:find|search|locate)\s+(?:all\s+)?(.+?)(?:\s+files?)?$',
                'action': 'search_files',
                'extract': ['file_type']
            },
            {
                'pattern': r'(?:organize|sort|arrange)\s+(.+?)(?:\s+by\s+(.+?))?$',
                'action': 'organize',
                'extract': ['location', 'criteria']
            },
            {
                'pattern': r'(?:move|copy)\s+(.+?)\s+(?:to|into)\s+(.+)',
                'action': 'move_copy',
                'extract': ['source', 'destination']
            },
            {
                'pattern': r'(?:delete|remove)\s+(.+)',
                'action': 'delete',
                'extract': ['target']
            },
            
            # Multi-step operations
            {
                'pattern': r'(?:list|show)\s+(.+?)\s+(?:in|to)\s+(.+)',
                'action': 'list_to_app',
                'extract': ['what', 'where']
            },
            {
                'pattern': r'(?:make|create)\s+(?:a\s+)?list\s+of\s+(.+?)\s+in\s+(.+)',
                'action': 'make_list',
                'extract': ['content', 'app']
            },
            
            # App operations
            {
                'pattern': r'open\s+(.+?)\s+(?:and|then)\s+(.+)',
                'action': 'open_and_do',
                'extract': ['app', 'action']
            },
            {
                'pattern': r'(?:search|find)\s+(.+?)\s+(?:in|on)\s+(.+)',
                'action': 'search_in_app',
                'extract': ['query', 'app']
            },
        ]
        
        # Common location mappings
        self.location_map = {
            'downloads': '~/Downloads',
            'download': '~/Downloads',
            'documents': '~/Documents',
            'document': '~/Documents',
            'desktop': '~/Desktop',
            'pictures': '~/Pictures',
            'picture': '~/Pictures',
            'videos': '~/Videos',
            'video': '~/Videos',
            'music': '~/Music',
            # Drive letters
            'd': 'D:\\',
            'd drive': 'D:\\',
            'd:': 'D:\\',
            'e': 'E:\\',
            'e drive': 'E:\\',
            'e:': 'E:\\',
            'c': 'C:\\',
            'c drive': 'C:\\',
            'c:': 'C:\\',
        }
    
    def _expand_location(self, location: str) -> str:
        """Expand location with smart logic"""
        if not location:
            return None
        
        location = location.strip().lower()
        
        # Check for drive pattern (like "d drive", "d:", "d")
        import re
        drive_match = re.match(r'^([a-z])\s*(?:drive|:)?$', location)
        if drive_match:
            drive_letter = drive_match.group(1).upper()
            return f"{drive_letter}:\\"
        
        # Map common names
        if location in self.location_map:
            return self.location_map[location]
        
        # If it looks like a path, return as-is
        if '\\' in location or '/' in location or ':' in location:
            return location
        
        # Default: try as-is
        return location
    
    def match(self, command: str) -> Optional[Dict]:
        """
        Try to match command to a template
        Returns: {action, params} or None
        """
        command_lower = command.lower().strip()
        
        # FIRST: Check for chained commands (and, then)
        # Smart Split: Only split if "and/then" is followed by a COMMAND VERB
        # This allows "search gravity and newton" (one query) vs "open chrome and search" (two commands)
        
        command_verbs = [
            "open", "close", "write", "list", "show", "find", "search", 
            "play", "pause", "stop", "click", "type", "make", "organize",
            "browse", "get", "create", "display"
        ]
        verbs_pattern = "|".join(command_verbs)
        
        # Regex: Matches " and " or " then " ONLY if followed by a command verb
        split_pattern = fr'\s+(?:and|then)\s+(?=(?:{verbs_pattern})\b)'
        
        if re.search(split_pattern, command_lower):
            parts = re.split(split_pattern, command_lower)
            # If we have multiple parts, we return a special "chain" action
            return {
                'action': 'chain_execution',
                'params': {'commands': parts}
            }
        
        for template in self.templates:
            match = re.search(template['pattern'], command_lower, re.IGNORECASE)
            if match:
                # Extract variables
                params = {}
                for i, var_name in enumerate(template['extract'], start=1):
                    if i <= len(match.groups()) and match.group(i):
                        value = match.group(i).strip()
                        
                        # Use smart expansion for locations
                        if var_name == 'location':
                            value = self._expand_location(value)
                        
                        params[var_name] = value
                
                return {
                    'action': template['action'],
                    'params': params
                }
        
        return None
    
    def execute(self, action: str, params: Dict) -> bool:
        """Execute matched action"""
        try:
            if action == 'chain_execution':
                return self._execute_chain(params.get('commands'))
            
            if action == 'list_files':
                return self._list_files(params.get('location'))
            
            elif action == 'search_files':
                return self._search_files(params.get('file_type'), params.get('location'))
            
            elif action == 'organize':
                return self._organize(params.get('location'))
            
            elif action == 'make_list':
                return self._make_list(params.get('content'), params.get('app'))
            
            elif action == 'list_to_app':
                return self._list_to_app(params.get('what'), params.get('where'))
            
            elif action == 'open_and_do':
                return self._open_and_do(params.get('app'), params.get('action'))
            
            elif action == 'search_in_app':
                return self._search_in_app(params.get('query'), params.get('app'))
            
            return False
        
        except Exception as e:
            self.vision.add_message("Error", f"Template execution failed: {str(e)[:80]}")
            return False
    
    # === EXECUTION METHODS ===
    
    def _list_files(self, location: Optional[str]) -> bool:
        """List files in location"""
        import os
        location = os.path.expanduser(location) if location else None
        files = self.vision.file_mgr.list_files(location)
        
        if files and 'error' not in files[0]:
            file_list = "\\n".join([f"{'📁' if f['type'] == 'folder' else '📄'} {f['name']}" 
                                   for f in files[:20]])
            self.vision.add_message("VISION", f"Files in {self.vision.file_mgr.current_directory}:\\n{file_list}")
            return True
        return False
    
    def _search_files(self, file_type: str, location: Optional[str] = None) -> bool:
        """Search for files"""
        results = self.vision.file_mgr.search_files(file_type, location)
        
        if results and 'error' not in results[0]:
            result_list = "\\n".join([f"📄 {r['name']} - {r['path']}" for r in results[:10]])
            self.vision.add_message("VISION", f"Found {len(results)} files:\\n{result_list}")
            return True
        return False
    
    def _organize(self, location: str) -> bool:
        """Organize files by type"""
        # Use existing organize_downloads logic
        if 'download' in location.lower():
            return self.vision.fast_complex.handle('organize downloads')
        return False
    
    def _make_list(self, content: str, app: str) -> bool:
        """Make a list of something in an app"""
        # Map to existing handler
        if 'download' in content and 'notepad' in app:
            return self.vision.fast_complex.handle('make a list of downloaded files in notepad')
        return False
    
    def _list_to_app(self, what: str, where: str) -> bool:
        """List something to an app"""
        if 'file' in what and 'notepad' in where:
            return self.vision.fast_complex.handle('make a list of files in notepad')
        return False
    
    def _open_and_do(self, app: str, action: str) -> bool:
        """Open app and do something"""
        import time
        # Open app
        success = self.vision.launch_app(app)
        if success:
            time.sleep(1)
            self.vision.add_message("VISION", f"✓ Opened {app}")
            
            # Execute action
            self.vision.process_command(action)
            return True
        return False
    
    def _execute_chain(self, commands: List[str]) -> bool:
        """Execute multiple commands in sequence"""
        self.vision.add_message("VISION", f"⛓️ Executing {len(commands)} chained commands...")
        
        for i, cmd in enumerate(commands, 1):
            self.vision.add_message("System", f"👉 Step {i}: {cmd}")
            # Process each command recursively through the main processor
            # This allows each part to be handled by templates, fast complex, or LLM
            self.vision.process_command(cmd)
            import time
            time.sleep(1) # Small delay between steps
            
        return True

    def _search_in_app(self, query: str, app: str) -> bool:
        """Search in specific app"""
        if 'chrome' in app or 'browser' in app:
            import os
            os.startfile(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            self.vision.add_message("VISION", f"✓ Searching '{query}' in browser")
            return True
        return False
