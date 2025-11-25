"""
Agent Memory System for VISION AI
Tracks command history, learns patterns, and remembers user preferences
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict, Counter

class AgentMemory:
    """Lightweight memory system that works on all devices"""
    
    def __init__(self, memory_file: str = "vision_memory.json"):
        self.memory_file = memory_file
        self.command_history = []  # Recent commands
        self.success_patterns = defaultdict(list)  # What worked
        self.failure_patterns = defaultdict(list)  # What failed
        self.user_preferences = {}  # Learned preferences
        self.app_usage = Counter()  # App usage frequency
        self.session_start = time.time()
        
        # Load existing memory
        self.load_memory()
    
    def load_memory(self):
        """Load memory from disk"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.command_history = data.get('command_history', [])[-100:]  # Keep last 100
                    self.success_patterns = defaultdict(list, data.get('success_patterns', {}))
                    self.failure_patterns = defaultdict(list, data.get('failure_patterns', {}))
                    self.user_preferences = data.get('user_preferences', {})
                    self.app_usage = Counter(data.get('app_usage', {}))
            except Exception as e:
                print(f"Failed to load memory: {e}")
    
    def save_memory(self):
        """Save memory to disk"""
        try:
            data = {
                'command_history': self.command_history[-100:],  # Save last 100
                'success_patterns': dict(self.success_patterns),
                'failure_patterns': dict(self.failure_patterns),
                'user_preferences': self.user_preferences,
                'app_usage': dict(self.app_usage),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save memory: {e}")
    
    def remember_command(self, command: str, success: bool, execution_time: float = 0, 
                        result: str = "", actions: List[Dict] = None):
        """Remember a command execution"""
        entry = {
            'command': command,
            'success': success,
            'timestamp': time.time(),
            'execution_time': execution_time,
            'result': result[:200],  # Truncate long results
            'actions': actions or []
        }
        
        self.command_history.append(entry)
        
        # Track patterns
        if success:
            self.success_patterns[command].append({
                'time': time.time(),
                'execution_time': execution_time,
                'actions': actions
            })
        else:
            self.failure_patterns[command].append({
                'time': time.time(),
                'result': result[:100]
            })
        
        # Extract app usage
        for word in command.lower().split():
            if word in ['chrome', 'notepad', 'calculator', 'vscode', 'spotify', 
                       'excel', 'word', 'outlook', 'teams']:
                self.app_usage[word] += 1
        
        # Auto-save every 10 commands
        if len(self.command_history) % 10 == 0:
            self.save_memory()
    
    def get_suggestions(self, partial_command: str) -> List[str]:
        """Get command suggestions based on history"""
        if not partial_command:
            return []
        
        suggestions = []
        partial_lower = partial_command.lower()
        
        # Find matching commands from history
        seen = set()
        for entry in reversed(self.command_history):
            cmd = entry['command']
            if cmd.lower().startswith(partial_lower) and cmd not in seen:
                suggestions.append(cmd)
                seen.add(cmd)
                if len(suggestions) >= 5:
                    break
        
        return suggestions
    
    def learn_preference(self, category: str, value: Any):
        """Learn a user preference"""
        self.user_preferences[category] = value
        self.save_memory()
    
    def get_preference(self, category: str, default: Any = None) -> Any:
        """Get a learned preference"""
        return self.user_preferences.get(category, default)
    
    def get_most_used_app(self) -> Optional[str]:
        """Get the user's most frequently used app"""
        if self.app_usage:
            return self.app_usage.most_common(1)[0][0]
        return None
    
    def get_similar_successful_commands(self, command: str) -> List[Dict]:
        """Find similar commands that succeeded"""
        results = []
        command_lower = command.lower()
        
        # Simple keyword matching
        keywords = set(command_lower.split())
        
        for cmd, executions in self.success_patterns.items():
            cmd_keywords = set(cmd.lower().split())
            overlap = len(keywords & cmd_keywords)
            
            if overlap >= 2:  # At least 2 matching words
                results.append({
                    'command': cmd,
                    'executions': len(executions),
                    'avg_time': sum(e['execution_time'] for e in executions) / len(executions),
                    'last_actions': executions[-1].get('actions', [])
                })
        
        # Sort by number of executions
        results.sort(key=lambda x: x['executions'], reverse=True)
        return results[:3]
    
    def should_suggest_automation(self, command: str) -> bool:
        """Check if a repetitive task should be automated"""
        # If command executed successfully 3+ times in last hour
        if command in self.success_patterns:
            recent = [e for e in self.success_patterns[command] 
                     if time.time() - e['time'] < 3600]  # Last hour
            return len(recent) >= 3
        return False
    
    def get_session_stats(self) -> Dict:
        """Get statistics for current session"""
        session_commands = [e for e in self.command_history 
                          if e['timestamp'] > self.session_start]
        
        successes = sum(1 for e in session_commands if e['success'])
        failures = len(session_commands) - successes
        
        return {
            'total_commands': len(session_commands),
            'successes': successes,
            'failures': failures,
            'success_rate': successes / len(session_commands) if session_commands else 0,
            'session_duration': time.time() - self.session_start
        }
    
    def clear_old_history(self, days: int = 30):
        """Clear command history older than N days"""
        cutoff = time.time() - (days * 86400)
        self.command_history = [e for e in self.command_history if e['timestamp'] > cutoff]
        
        # Clean up patterns
        for cmd in list(self.success_patterns.keys()):
            self.success_patterns[cmd] = [e for e in self.success_patterns[cmd] if e['time'] > cutoff]
            if not self.success_patterns[cmd]:
                del self.success_patterns[cmd]
        
        for cmd in list(self.failure_patterns.keys()):
            self.failure_patterns[cmd] = [e for e in self.failure_patterns[cmd] if e['time'] > cutoff]
            if not self.failure_patterns[cmd]:
                del self.failure_patterns[cmd]
        
        self.save_memory()
