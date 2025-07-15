#\!/usr/bin/env python3
"""Debug de rotación manual"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10)

# Crear macro
macro_id = engine.create_macro("test_debug", 1, "rigid")
sid = list(engine._macros[macro_id].source_ids)[0]
engine._positions[sid] = np.array([5.0, 0.0, 0.0])

print(f"Source ID: {sid}")
print(f"Posición inicial: {engine._positions[sid]}")

# Verificar motion_states
if sid in engine.motion_states:
    motion = engine.motion_states[sid]
    print(f"Motion state existe para source {sid}")
    print(f"Active components: {list(motion.active_components.keys())}")
else:
    print(f"NO hay motion state para source {sid}")

# Aplicar rotación
print("\nAplicando rotación manual...")
engine.set_manual_macro_rotation(
    macro_id,
    yaw=np.radians(90),
    pitch=0,
    roll=0
)

# Verificar componentes después
if sid in engine.motion_states:
    motion = engine.motion_states[sid]
    print(f"Active components después: {list(motion.active_components.keys())}")
    
    if 'manual_macro_rotation' in motion.active_components:
        comp = motion.active_components['manual_macro_rotation']
        print(f"  Componente habilitado: {comp.enabled}")
        print(f"  Target yaw: {np.degrees(comp.target_yaw)}")
        print(f"  First update: {comp.first_update}")
