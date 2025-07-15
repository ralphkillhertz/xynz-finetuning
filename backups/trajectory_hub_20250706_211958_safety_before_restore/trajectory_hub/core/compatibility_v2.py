"""
Capa de compatibilidad V2 - Para componentes update-based
"""
import json
import os
import numpy as np
from typing import Dict, List, Optional, Tuple

class CompatibilityManagerV2:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.config_path = os.path.join("trajectory_hub", "config", "parallel_config.json")
            self.load_config()
            self.initialized = True
            self.pending_deltas = {}  # Deltas pendientes por source_id
    
    def load_config(self):
        """Load configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"PARALLEL_MODE": False, "CONCENTRATION_DUAL_MODE": False}
    
    def reload_config(self):
        """Force reload"""
        self.load_config()
    
    def is_concentration_dual_mode(self):
        """Check if concentration should use dual mode"""
        return self.config.get("CONCENTRATION_DUAL_MODE", False)
    
    def calculate_position_delta(self, current_pos: np.ndarray, target_pos: np.ndarray, strength: float) -> np.ndarray:
        """Calculate position delta instead of final position"""
        # En modo normal: new_pos = lerp(current, target, strength)
        # En modo delta: delta = (target - current) * strength
        return (target_pos - current_pos) * strength
    
    def store_pending_delta(self, source_id: int, component_name: str, position_delta: np.ndarray):
        """Store delta for later application"""
        if source_id not in self.pending_deltas:
            self.pending_deltas[source_id] = []
        
        self.pending_deltas[source_id].append({
            'component': component_name,
            'position_delta': position_delta,
            'timestamp': datetime.now().isoformat()
        })
        
        if self.config.get("LOG_DELTAS", False):
            delta_norm = np.linalg.norm(position_delta)
            print(f"  [DELTA] Source {source_id} - {component_name}: |Δ|={delta_norm:.4f}")
    
    def get_accumulated_delta(self, source_id: int) -> Optional[np.ndarray]:
        """Get sum of all pending deltas for a source"""
        if source_id not in self.pending_deltas:
            return None
        
        deltas = self.pending_deltas[source_id]
        if not deltas:
            return None
        
        # Sum all position deltas
        total_delta = np.zeros(3)
        for delta_info in deltas:
            total_delta += delta_info['position_delta']
        
        return total_delta
    
    def clear_deltas(self, source_id: Optional[int] = None):
        """Clear pending deltas"""
        if source_id is None:
            self.pending_deltas.clear()
        elif source_id in self.pending_deltas:
            del self.pending_deltas[source_id]
    
    def apply_accumulated_deltas(self, state, source_id: int):
        """Apply all accumulated deltas to state"""
        total_delta = self.get_accumulated_delta(source_id)
        if total_delta is not None:
            state.position += total_delta
            self.clear_deltas(source_id)
        return state

# Global instance
compat_v2 = CompatibilityManagerV2()

# For backward compatibility
compat = compat_v2

from datetime import datetime
