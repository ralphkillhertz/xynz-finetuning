"""
Capa de compatibilidad para transición gradual - Phase 1
"""
import json
import os
import numpy as np

class CompatibilityManager:
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
            self.delta_storage = {}  # Store deltas per source
    
    def load_config(self):
        """Load current configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"PARALLEL_MODE": False, "CONCENTRATION_DUAL_MODE": False}
    
    def reload_config(self):
        """Force reload configuration"""
        self.load_config()
    
    def is_concentration_dual_mode(self):
        """Check if concentration should use dual mode"""
        return self.config.get("CONCENTRATION_DUAL_MODE", False)
    
    def store_delta(self, source_id, component_name, position_delta, orientation_delta=None):
        """Store delta for later application"""
        if source_id not in self.delta_storage:
            self.delta_storage[source_id] = []
        
        self.delta_storage[source_id].append({
            'component': component_name,
            'position': position_delta,
            'orientation': orientation_delta
        })
        
        if self.config.get("LOG_DELTAS", False):
            print(f"  [DELTA] Source {source_id} - {component_name}: pos_delta={position_delta}")
    
    def get_deltas(self, source_id):
        """Get all stored deltas for a source"""
        return self.delta_storage.get(source_id, [])
    
    def clear_deltas(self, source_id=None):
        """Clear stored deltas"""
        if source_id is None:
            self.delta_storage.clear()
        elif source_id in self.delta_storage:
            del self.delta_storage[source_id]
    
    def apply_deltas(self, motion):
        """Apply all accumulated deltas to motion"""
        source_id = getattr(motion, 'source_id', 0)
        deltas = self.get_deltas(source_id)
        
        for delta_info in deltas:
            if delta_info['position'] is not None:
                motion.state.position += delta_info['position']
            if delta_info['orientation'] is not None:
                motion.state.orientation += delta_info['orientation']
        
        # Clear after applying
        self.clear_deltas(source_id)

# Global instance
compat = CompatibilityManager()
