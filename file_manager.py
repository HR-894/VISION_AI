"""
File Manager for VISION AI
Handles file system operations with safety checks
"""

import os
import shutil
import glob
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import send2trash
from datetime import datetime, timedelta

class FileManager:
    """Manages file system operations safely"""
    
    def __init__(self, safety_guard):
        self.safety_guard = safety_guard
        self.current_directory = os.path.expanduser('~')  # Start at user home
    
    def list_files(self, directory: Optional[str] = None, pattern: str = '*') -> List[Dict[str, str]]:
        """List files in directory with details"""
        target_dir = directory or self.current_directory
        
        # Validate path
        allowed, reason = self.safety_guard.validate_file_operation('list', target_dir)
        if not allowed:
            return [{'error': reason}]
        
        try:
            files = []
            path = Path(target_dir)
            
            if not path.exists():
                return [{'error': f"Directory not found: {target_dir}"}]
            
            self.current_directory = str(path.absolute())
            
            for item in path.glob(pattern):
                try:
                    stat = item.stat()
                    files.append({
                        'name': item.name,
                        'path': str(item.absolute()),
                        'type': 'folder' if item.is_dir() else 'file',
                        'size': self._format_size(stat.st_size) if item.is_file() else '',
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                    })
                except:
                    continue
            
            return sorted(files, key=lambda x: (x['type'] != 'folder', x['name'].lower()))
        
        except Exception as e:
            return [{'error': f"Failed to list files: {str(e)}"}]
    
    def copy_file(self, source: str, destination: str) -> Tuple[bool, str]:
        """Copy file or directory"""
        # Validate paths
        allowed_src, reason_src = self.safety_guard.validate_file_operation('copy', source)
        allowed_dst, reason_dst = self.safety_guard.validate_file_operation('copy', destination)
        
        if not allowed_src:
            return False, reason_src
        if not allowed_dst:
            return False, reason_dst
        
        try:
            if os.path.isdir(source):
                shutil.copytree(source, destination)
                msg = f"✓ Copied folder: {os.path.basename(source)}"
            else:
                shutil.copy2(source, destination)
                msg = f"✓ Copied file: {os.path.basename(source)}"
            
            self.safety_guard.log_action('COPY', f"{source} → {destination}", 'SUCCESS')
            return True, msg
        
        except Exception as e:
            self.safety_guard.log_action('COPY', f"{source} → {destination}", f'FAILED: {str(e)}')
            return False, f"✗ Copy failed: {str(e)}"
    
    def move_file(self, source: str, destination: str) -> Tuple[bool, str]:
        """Move file or directory"""
        # Validate paths
        allowed_src, reason_src = self.safety_guard.validate_file_operation('move', source)
        allowed_dst, reason_dst = self.safety_guard.validate_file_operation('move', destination)
        
        if not allowed_src:
            return False, reason_src
        if not allowed_dst:
            return False, reason_dst
        
        try:
            shutil.move(source, destination)
            msg = f"✓ Moved: {os.path.basename(source)}"
            self.safety_guard.log_action('MOVE', f"{source} → {destination}", 'SUCCESS')
            return True, msg
        
        except Exception as e:
            self.safety_guard.log_action('MOVE', f"{source} → {destination}", f'FAILED: {str(e)}')
            return False, f"✗ Move failed: {str(e)}"
    
    def rename_file(self, old_path: str, new_name: str) -> Tuple[bool, str]:
        """Rename file or directory"""
        allowed, reason = self.safety_guard.validate_file_operation('rename', old_path)
        if not allowed:
            return False, reason
        
        try:
            directory = os.path.dirname(old_path)
            new_path = os.path.join(directory, new_name)
            
            os.rename(old_path, new_path)
            msg = f"✓ Renamed to: {new_name}"
            self.safety_guard.log_action('RENAME', f"{old_path} → {new_name}", 'SUCCESS')
            return True, msg
        
        except Exception as e:
            self.safety_guard.log_action('RENAME', f"{old_path} → {new_name}", f'FAILED: {str(e)}')
            return False, f"✗ Rename failed: {str(e)}"
    
    def delete_to_recycle(self, path: str) -> Tuple[bool, str]:
        """Delete file/folder to recycle bin (SAFE deletion)"""
        allowed, reason = self.safety_guard.validate_file_operation('delete', path)
        if not allowed:
            return False, reason
        
        try:
            if not os.path.exists(path):
                return False, f"✗ File not found: {path}"
            
            # Use send2trash for safe deletion
            send2trash.send2trash(path)
            msg = f"✓ Moved to Recycle Bin: {os.path.basename(path)}"
            self.safety_guard.log_action('DELETE (Recycle Bin)', path, 'SUCCESS')
            return True, msg
        
        except Exception as e:
            self.safety_guard.log_action('DELETE', path, f'FAILED: {str(e)}')
            return False, f"✗ Delete failed: {str(e)}"
    
    def search_files(self, pattern: str, directory: Optional[str] = None, 
                    file_type: Optional[str] = None, 
                    days_old: Optional[int] = None) -> List[Dict[str, str]]:
        """Search for files by pattern, type, or age"""
        search_dir = directory or self.current_directory
        
        allowed, reason = self.safety_guard.validate_file_operation('search', search_dir)
        if not allowed:
            return [{'error': reason}]
        
        results = []
        try:
            search_path = Path(search_dir)
            
            # Build search pattern
            if file_type:
                search_pattern = f"**/*.{file_type}"
            else:
                search_pattern = f"**/*{pattern}*"
            
            for item in search_path.glob(search_pattern):
                try:
                    stat = item.stat()
                    modified_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    # Filter by age if specified
                    if days_old is not None:
                        age = datetime.now() - modified_time
                        if age.days > days_old:
                            continue
                    
                    # Filter by name pattern if searching by type
                    if file_type and pattern.lower() not in item.name.lower():
                        continue
                    
                    results.append({
                        'name': item.name,
                        'path': str(item.absolute()),
                        'type': 'folder' if item.is_dir() else 'file',
                        'size': self._format_size(stat.st_size) if item.is_file() else '',
                        'modified': modified_time.strftime('%Y-%m-%d %H:%M')
                    })
                except:
                    continue
            
            return results[:100]  # Limit to 100 results
        
        except Exception as e:
            return [{'error': f"Search failed: {str(e)}"}]
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_directory_info(self, directory: Optional[str] = None) -> Dict[str, any]:
        """Get directory statistics"""
        target_dir = directory or self.current_directory
        
        try:
            path = Path(target_dir)
            items = list(path.iterdir())
            
            files = [i for i in items if i.is_file()]
            folders = [i for i in items if i.is_dir()]
            
            total_size = sum(f.stat().st_size for f in files)
            
            return {
                'path': str(path.absolute()),
                'total_items': len(items),
                'files': len(files),
                'folders': len(folders),
                'total_size': self._format_size(total_size)
            }
        except Exception as e:
            return {'error': str(e)}
