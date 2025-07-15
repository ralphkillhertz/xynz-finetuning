#!/usr/bin/env python3
"""Simple debug para ver el flujo del engine"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def simple_debug():
    """Simple debug"""
    print("=== SIMPLE DEBUG ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    macro_id = engine.create_macro("simple_debug", 1, "line")
    
    engine.set_macro_trajectory(
        macro_id,
        "circle",
        speed=1.0,
        radius=5.0,
        playback_mode="fix"
    )
    
    print("Haciendo update con dt = 0.1...")
    engine.update(0.1)
    print("Update completado")

if __name__ == "__main__":
    simple_debug()