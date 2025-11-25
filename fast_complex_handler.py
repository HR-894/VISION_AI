"""
Fast Multi-Step Command Handlers - NO LLM NEEDED!
Uses pattern matching for common complex commands
"""

import os
import time
import re
from typing import Optional, Tuple

class FastComplexHandler:
    """Handles complex commands with pattern matching (no LLM delay)"""
    
    def __init__(self, vision_ai):
        self.vision = vision_ai
    
    def handle(self, text: str) -> Optional[bool]:
        """
        Try to handle complex command with fast pattern matching
        Returns True if handled, False if not recognized, None if failed
        """
        text_lower = text.lower().strip()
        
        # === PATTERN 1: List files in notepad ===
        if re.search(r'(?:make|create|write)\s+(?:a\s+)?list.*(?:file|download).*notepad', text_lower):
            return self._list_files_in_notepad(text_lower)
        
        # === PATTERN 2: Organize downloads ===
        if re.search(r'organize.*download', text_lower):
            return self._organize_downloads()
        
        # === PATTERN 3: Find and move files ===
        match = re.search(r'find\s+(?:all\s+)?(.+?)\s+(?:and\s+)?move.*?(?:to\s+)?(\w+)', text_lower)
        if match:
            file_type = match.group(1)
            destination = match.group(2)
            return self._find_and_move(file_type, destination)
        
        # === PATTERN 4: Open app and search ===
        if re.search(r'open\s+(\w+).*search\s+(.+)', text_lower):
            match = re.search(r'open\s+(\w+).*search\s+(.+)', text_lower)
            app = match.group(1)
            query = match.group(2)
            return self._open_and_search(app, query)
        
        return False  # Not recognized
    
    def _list_files_in_notepad(self, text: str) -> bool:
        """List downloads in notepad"""
        try:
            self.vision.add_message("VISION", "📋 Step 1/3: Getting downloads list...")
            
            # Get downloads
            downloads = os.path.expanduser('~/Downloads')
            files = self.vision.file_mgr.list_files(downloads)
            
            if not files or 'error' in files[0]:
                self.vision.add_message("Error", "Failed to list downloads")
                return None
            
            self.vision.add_message("VISION", f"✓ Found {len(files)} files")
            time.sleep(0.5)
            
            # Open notepad
            self.vision.add_message("VISION", "📋 Step 2/3: Opening notepad...")
            import subprocess
            subprocess.Popen(['notepad.exe'])
            time.sleep(2)  # Wait for notepad to open
            self.vision.add_message("VISION", "✓ Notepad opened")
            
            # Type the list
            self.vision.add_message("VISION", "📋 Step 3/3: Writing file list...")
            file_list = "Downloads File List:\\n\\n"
            for f in files[:50]:  # Limit to 50 files
                file_list += f"{f['name']}\\n"
            
            self.vision.window_mgr.type_text(file_list, interval=0.01)
            self.vision.add_message("VISION", f"✓ Wrote {min(len(files), 50)} filenames to notepad!")
            
            return True
        
        except Exception as e:
            self.vision.add_message("Error", f"Failed: {str(e)[:100]}")
            return None
    
    def _organize_downloads(self) -> bool:
        """Organize downloads by file type"""
        try:
            self.vision.add_message("VISION", "📂 Organizing downloads by type...")
            
            downloads = os.path.expanduser('~/Downloads')
            files = self.vision.file_mgr.list_files(downloads)
            
            if not files or 'error' in files[0]:
                return None
            
            # Create folders
            folders = {
                'PDFs': ['.pdf'],
                'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
                'Documents': ['.doc', '.docx', '.txt', '.xlsx', '.pptx'],
                'Videos': ['.mp4', '.avi', '.mkv', '.mov'],
                'Archives': ['.zip', '.rar', '.7z']
            }
            
            moved = 0
            for folder_name, extensions in folders.items():
                folder_path = os.path.join(downloads, folder_name)
                os.makedirs(folder_path, exist_ok=True)
            
            for file in files:
                if file['type'] == 'file':
                    ext = os.path.splitext(file['name'])[1].lower()
                    for folder_name, extensions in folders.items():
                        if ext in extensions:
                            try:
                                source = file['path']
                                dest = os.path.join(downloads, folder_name, file['name'])
                                import shutil
                                shutil.move(source, dest)
                                moved += 1
                            except:
                                pass
            
            self.vision.add_message("VISION", f"✓ Organized {moved} files into folders!")
            return True
        
        except Exception as e:
            self.vision.add_message("Error", f"Failed: {str(e)[:100]}")
            return None
    
    def _find_and_move(self, file_type: str, destination: str) -> bool:
        """Find files and move them"""
        try:
            self.vision.add_message("VISION", f"🔍 Finding {file_type} files...")
            results = self.vision.file_mgr.search_files(file_type)
            
            if not results or 'error' in results[0]:
                self.vision.add_message("VISION", f"No {file_type} files found")
                return True
            
            # Map common destinations
            dest_map = {
                'desktop': os.path.expanduser('~/Desktop'),
                'documents': os.path.expanduser('~/Documents'),
                'downloads': os.path.expanduser('~/Downloads')
            }
            
            dest_path = dest_map.get(destination, destination)
            moved = 0
            
            for file in results[:10]:  # Limit to 10 files
                try:
                    self.vision.file_mgr.move_file(file['path'], dest_path)
                    moved += 1
                except:
                    pass
            
            self.vision.add_message("VISION", f"✓ Moved {moved} files to {destination}")
            return True
        
        except Exception as e:
            self.vision.add_message("Error", f"Failed: {str(e)[:100]}")
            return None
    
    def _open_and_search(self, app: str, query: str) -> bool:
        """Open app and search"""
        try:
            # Open app
            self.vision.add_message("VISION", f"📂 Opening {app}...")
            self.vision.launch_app(app)
            time.sleep(2)
            
            # Type search query
            self.vision.add_message("VISION", f"🔍 Searching for '{query}'...")
            self.vision.window_mgr.type_text(query)
            time.sleep(0.5)
            self.vision.window_mgr.press_key('enter')
            
            self.vision.add_message("VISION", f"✓ Searched for '{query}' in {app}")
            return True
        
        except Exception as e:
            self.vision.add_message("Error", f"Failed: {str(e)[:100]}")
            return None
