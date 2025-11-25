"""
Hybrid LLM Controller for VISION AI
Uses Qwen2-0.5B for fast command parsing with GPU acceleration
"""

import json
import os
import time
from typing import List, Dict, Optional, Any
from llama_cpp import Llama

class LLMController:
    """Handles command parsing using Qwen2-0.5B with Hybrid GPU/CPU execution"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path
        self.is_loaded = False
        self.gpu_layers = 0
        
        # Detect GPU availability (Simple check)
        self._detect_gpu()
        
    def _detect_gpu(self):
        """Detect if GPU is available and set layers accordingly"""
        try:
            # Try to load a tiny dummy model or check libraries
            # For now, we'll assume if llama-cpp-python is installed with CUBLAS, it works
            # We'll default to hybrid mode (offload some layers)
            # Qwen2-0.5B is tiny, so we can probably offload ALL layers if GPU exists
            # or a good chunk if it's a weak GPU.
            
            # Heuristic: Try to offload all layers (33 for Qwen2-0.5B)
            # If it fails during load, we can fallback, but llama-cpp usually handles it.
            self.gpu_layers = 35 # Offload everything for speed
            print(f"GPU Configuration: Attempting to offload {self.gpu_layers} layers")
        except Exception:
            self.gpu_layers = 0
            print("GPU Detection failed, defaulting to CPU")

    def load_model(self):
        """Lazy load model only when needed"""
        if self.is_loaded:
            return True
        
        if not self.model_path or not os.path.exists(self.model_path):
            print(f"ERROR: Model not found: {self.model_path}")
            return False
        
        try:
            print(f"Loading Llama-3.2-1B model (GPU Layers: {self.gpu_layers})...")
            start_time = time.time()
            
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=2048,         # Larger context for complex task planning
                n_threads=6,        # CPU threads
                n_gpu_layers=self.gpu_layers, # GPU acceleration
                n_batch=512,
                verbose=False,
                use_mmap=True,
                use_mlock=False
            )
            
            self.is_loaded = True
            load_time = time.time() - start_time
            print(f"Model loaded in {load_time:.2f}s")
            return True
        except Exception as e:
            print(f"ERROR: Failed to load model: {str(e)}")
            # Fallback to CPU if GPU load fails
            if self.gpu_layers > 0:
                print("Retrying with CPU only...")
                self.gpu_layers = 0
                return self.load_model()
            return False
    
    def parse_ambiguous_command(self, command: str, context: str = "") -> Optional[List[Dict[str, Any]]]:
        """
        Parse a command that templates couldn't handle.
        Uses Llama-3.2-1B for smart command understanding and multi-step planning.
        STRICTLY command-focused - NO chatting, NO explanations, ONLY action plans.
        """
        if not self.load_model():
            return None
            
        # ENHANCED PROMPT: Command Parser + Task Planner (NO CHATTING)
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a COMMAND EXECUTION PLANNER. Your ONLY job is to convert user commands into executable action plans.

RULES:
1. OUTPUT ONLY JSON - no explanations, no chatting
2. Break complex commands into simple sequential steps
3. Each step is ONE atomic action
4. Use ONLY these actions: open_app, type_text, press_key, search_web, list_files, open_file, create_folder, move_file, copy_file, wait

Available Actions:
- open_app: {{"app": "chrome|notepad|calculator|etc"}}
- open_file: {{"path": "C:\\\\path\\\\to\\\\file.txt"}}
- type_text: {{"text": "text to type"}}
- press_key: {{"key": "enter|tab|ctrl+c|etc"}}
- search_web: {{"query": "search terms", "engine": "google|youtube"}}
- list_files: {{"directory": "path"}}
- create_folder: {{"path": "path"}}
- wait: {{"seconds": 1}}

EXAMPLES:

Command: "list downloads to google keep"
Plan:
[
  {{"action": "list_files", "params": {{"directory": "~/Downloads"}}}},
  {{"action": "open_app", "params": {{"app": "chrome"}}}},
  {{"action": "wait", "params": {{"seconds": 2}}}},
  {{"action": "search_web", "params": {{"query": "keep.google.com", "engine": "google"}}}},
  {{"action": "wait", "params": {{"seconds": 2}}}},
  {{"action": "type_text", "params": {{"text": "[FILES_LIST_PLACEHOLDER]"}}}}
]

Command: "open notepad and write hello"
Plan:
[
  {{"action": "open_app", "params": {{"app": "notepad"}}}},
  {{"action": "wait", "params": {{"seconds": 1}}}},
  {{"action": "type_text", "params": {{"text": "hello"}}}}
]

Command: "search keep notes and write something"
Plan:
[
  {{"action": "search_web", "params": {{"query": "keep notes", "engine": "google"}}}},
  {{"action": "wait", "params": {{"seconds": 2}}}},
  {{"action": "type_text", "params": {{"text": "something"}}}}
]

OUTPUT FORMAT: JSON array of actions ONLY. No text before or after.<|eot_id|><|start_header_id|>user<|end_header_id|>

Context: {context}
Command: {command}

Output JSON plan:<|eot_id|><|start_header_id|>assistant<|end_header_id|>

["""
        
        try:
            start_time = time.time()
            response = self.model(
                prompt,
                max_tokens=512,  # More tokens for complex plans
                temperature=0.1,  # Low temperature for consistent output
                stop=["<|eot_id|>", "<|end_of_text|>", "```"],
                echo=False
            )
            
            output = response['choices'][0]['text'].strip()
            inference_time = time.time() - start_time
            print(f"LLM Task Planning: {inference_time:.2f}s")
            
            # Clean up potential markdown or extra text
            if "```json" in output:
                output = output.split("```json")[1].split("```")[0].strip()
            elif "```" in output:
                output = output.split("```")[1].split("```")[0].strip()
            
            # Extract JSON array if there's extra text
            if not output.startswith('['):
                start = output.find('[')
                end = output.rfind(']') + 1
                if start >= 0 and end > 0:
                    output = output[start:end]
                
            return self._parse_json(output)
            
        except Exception as e:
            print(f"ERROR: LLM planning failed: {str(e)}")
            return None

    def _parse_json(self, text: str) -> Optional[List[Dict[str, Any]]]:
        try:
            # Try to find array brackets if there's extra text
            start = text.find('[')
            end = text.rfind(']') + 1
            if start >= 0 and end > 0:
                text = text[start:end]
            return json.loads(text)
        except:
            return None
