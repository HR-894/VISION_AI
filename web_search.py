"""
Web Search Integration for VISION AI
No API keys needed - uses DuckDuckGo Instant Answer API
"""

import json
import urllib.parse
import urllib.request
from typing import Optional, Dict, List

class WebSearch:
    """Lightweight web search - works on all devices"""
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.timeout = 5  # seconds
    
    def search(self, query: str) -> Dict:
        """
        Search DuckDuckGo and return instant answer
        Returns: {
            'answer': str,  # Direct answer if available
            'abstract': str,  # Wikipedia summary
            'related': List[str],  # Related topics
            'url': str  # Source URL
        }
        """
        try:
            # Build URL
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
            
            # Make request
            req = urllib.request.Request(url, headers={'User-Agent': 'VISION-AI/1.0'})
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            # Extract useful info
            result = {
                'answer': data.get('Answer', ''),
                'abstract': data.get('AbstractText', ''),
                'definition': data.get('Definition', ''),
                'related': [t['Text'] for t in data.get('RelatedTopics', [])[:5] if isinstance(t, dict) and 'Text' in t],
                'url': data.get('AbstractURL', '')
            }
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'answer': '',
                'abstract': '',
                'related': [],
                'url': ''
            }
    
    def get_quick_answer(self, query: str) -> Optional[str]:
        """Get a quick answer to a query"""
        result = self.search(query)
        
        # Try different fields in order of priority
        if result.get('answer'):
            return result['answer']
        elif result.get('definition'):
            return result['definition']
        elif result.get('abstract'):
            # Truncate long abstracts
            abstract = result['abstract']
            if len(abstract) > 300:
                abstract = abstract[:297] + "..."
            return abstract
        
        return None
    
    def enhance_command_with_context(self, command: str) -> Optional[str]:
        """
        Enhance a command with web context
        Useful for ambiguous commands
        """
        # Extract potential search terms
        # e.g., "who is elon musk" -> search "elon musk"
        search_patterns = [
            ("who is ", ""),
            ("what is ", ""),
            ("where is ", ""),
            ("when is ", ""),
            ("how to ", "how to "),
        ]
        
        for pattern, replacement in search_patterns:
            if command.lower().startswith(pattern):
                search_query = command[len(pattern):]
                answer = self.get_quick_answer(search_query)
                if answer:
                    return f"Context: {answer}"
        
        return None
