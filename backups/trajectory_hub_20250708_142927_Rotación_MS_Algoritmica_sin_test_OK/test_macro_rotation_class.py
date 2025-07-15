#!/usr/bin/env python3
"""Test directo de la clase MacroRotation"""

import numpy as np
from trajectory_hub.core.motion_components import MacroRotation, MotionState, MotionDelta

print("🧪 Test directo de MacroRotation")

# Crear instancia
rot = MacroRotation()
print(f"✅ MacroRotation creada")

# Verificar métodos
methods = [m for m in dir(rot) if not m.startswith('_')]
print(f"\nMétodos disponibles:")
for m in methods:
    print(f"  - {m}")

# Probar set_rotation si existe
if hasattr(rot, 'set_rotation'):
    print("\n✅ set_rotation existe")
    rot.set_rotation(speed_x=0, speed_y=1.0, speed_z=0)
    print(f"  Enabled: {rot.enabled}")
    print(f"  Speed Y: {rot.speed_y}")
else:
    print("\n❌ set_rotation NO existe")

# Probar calculate_delta
if hasattr(rot, 'calculate_delta'):
    print("\n✅ calculate_delta existe")
    state = MotionState()
    state.position = np.array([1.0, 0.0, 0.0])
    
    delta = rot.calculate_delta(state, 0.0, 0.016)  # 1/60 segundo
    print(f"  Delta: {delta.position if hasattr(delta, 'position') else 'No position'}")
