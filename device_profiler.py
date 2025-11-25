"""
Device Profiler for VISION AI
Auto-detects hardware capabilities and selects optimal models
"""

import psutil
import platform
from typing import Dict, Tuple

class DeviceProfiler:
    """Detect hardware and configure optimal settings"""
    
    def __init__(self):
        self.profile = self._detect_hardware()
        self.tier = self._determine_tier()
    
    def _detect_hardware(self) -> Dict:
        """Detect system hardware"""
        try:
            # RAM
            ram = psutil.virtual_memory()
            ram_gb = ram.total / (1024**3)
            
            # CPU
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            cpu_ghz = cpu_freq.current / 1000 if cpu_freq else 0
            
            # Storage
            disk = psutil.disk_usage('/')
            storage_gb = disk.total / (1024**3)
            
            # GPU Detection (simple check)
            has_gpu = self._check_gpu()
            
            return {
                'ram_gb': ram_gb,
                'cpu_count': cpu_count,
                'cpu_ghz': cpu_ghz,
                'storage_gb': storage_gb,
                'has_gpu': has_gpu,
                'os': platform.system(),
                'os_version': platform.version()
            }
        except Exception as e:
            # Fallback defaults
            return {
                'ram_gb': 8,
                'cpu_count': 4,
                'cpu_ghz': 2.0,
                'storage_gb': 100,
                'has_gpu': False,
                'os': 'Windows',
                'os_version': 'Unknown'
            }
    
    def _check_gpu(self) -> bool:
        """Simple GPU detection"""
        try:
            import subprocess
            # Check for NVIDIA GPU
            result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=2)
            return result.returncode == 0
        except:
            return False
    
    def _determine_tier(self) -> str:
        """Determine device tier based on hardware"""
        ram = self.profile['ram_gb']
        cpu = self.profile['cpu_count']
        gpu = self.profile['has_gpu']
        
        # Tier 3: High-end (16GB+ RAM, GPU)
        if ram >= 16 and gpu:
            return 'high'
        
        # Tier 2: Mid-range (8-16GB RAM, good CPU)
        elif ram >= 8 and cpu >= 6:
            return 'mid'
        
        # Tier 1: Low-end (4-8GB RAM)
        else:
            return 'low'
    
    def get_optimal_models(self) -> Dict[str, str]:
        """Get optimal model configuration for this device"""
        tier = self.tier
        
        if tier == 'high':
            return {
                'whisper': 'large-v3',    # Best accuracy
                'llm': 'Qwen2.5-7B',      # Best reasoning (if available)
                'llm_fallback': 'Llama-3.2-3B',
                'vision': 'Qwen2-VL-2B',  # Vision model
                'gpu_layers': 50          # Offload to GPU
            }
        elif tier == 'mid':
            return {
                'whisper': 'large-v3',    # Best accuracy still fits
                'llm': 'Llama-3.2-3B',    # Good balance
                'llm_fallback': 'Llama-3.2-1B',
                'vision': None,           # Skip vision model
                'gpu_layers': 0           # CPU only
            }
        else:  # low
            return {
                'whisper': 'medium',      # Balance accuracy/size
                'llm': 'Llama-3.2-1B',    # Lightweight
                'llm_fallback': None,
                'vision': None,
                'gpu_layers': 0
            }
    
    def get_performance_config(self) -> Dict:
        """Get performance configuration"""
        tier = self.tier
        cpu_count = self.profile['cpu_count']
        
        return {
            'whisper_threads': min(cpu_count, 8),
            'llm_threads': max(cpu_count - 2, 4),
            'llm_context': 2048 if tier != 'low' else 1024,
            'enable_caching': True,
            'cache_size_mb': 500 if tier == 'high' else 200,
            'preload_models': tier == 'high',
            'lazy_load_llm': tier == 'low'
        }
    
    def print_profile(self):
        """Print device profile"""
        print(f"\n{'='*50}")
        print(f"Device Profile: {self.tier.upper()}-END")
        print(f"{'='*50}")
        print(f"RAM: {self.profile['ram_gb']:.1f} GB")
        print(f"CPU: {self.profile['cpu_count']} cores @ {self.profile['cpu_ghz']:.1f} GHz")
        print(f"GPU: {'Available' if self.profile['has_gpu'] else 'Not detected'}")
        print(f"Storage: {self.profile['storage_gb']:.1f} GB")
        print(f"OS: {self.profile['os']} {self.profile['os_version'][:20]}")
        
        models = self.get_optimal_models()
        print(f"\nOptimal Configuration:")
        print(f"  Whisper: {models['whisper']}")
        print(f"  LLM: {models['llm']}")
        if models.get('vision'):
            print(f"  Vision: {models['vision']}")
        print(f"  GPU Layers: {models['gpu_layers']}")
        print(f"{'='*50}\n")
        
        return self.tier
    
    def should_use_feature(self, feature: str) -> bool:
        """Check if a feature should be enabled on this device"""
        tier = self.tier
        
        feature_requirements = {
            'vision_llm': 'high',
            'large_llm': 'mid',
            'aggressive_caching': 'mid',
            'preload_models': 'high',
            'background_indexing': 'mid'
        }
        
        required = feature_requirements.get(feature)
        if not required:
            return True  # Feature has no requirements
        
        tier_order = {'low': 0, 'mid': 1, 'high': 2}
        return tier_order.get(tier, 0) >= tier_order.get(required, 0)
