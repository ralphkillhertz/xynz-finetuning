#!/usr/bin/env python3
"""Test mínimo con debug paso a paso"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import MacroRotation, MotionState

print("🧪 Test Mínimo MacroRotation")

# Probar MacroRotation directamente
print("\n1️⃣ Test directo de MacroRotation:")
rot = MacroRotation()
rot.speed_y = 1.0
rot.enabled = True
rot.center = np.array([0, 0, 0])

state = MotionState()
state.position = np.array([1.0, 0.0, 0.0])

print(f"  Posición inicial: {state.position}")
delta = rot.calculate_delta(state, 0.0, 0.016)
print(f"  Delta calculado: {delta.position}")
print(f"  Posición esperada: {state.position + delta.position}")

# Probar con el engine
print("\n2️⃣ Test con engine:")
engine = EnhancedTrajectoryEngine()
engine.create_source(0)
engine._positions[0] = np.array([1.0, 0.0, 0.0])

# Configurar rotación manualmente
if 0 in engine.motion_states:
    motion = engine.motion_states[0]
    rot = MacroRotation()
    rot.speed_y = 1.0
    rot.enabled = True
    rot.center = np.array([0, 0, 0])
    motion.active_components['macro_rotation'] = rot
    print("  ✅ Rotación configurada manualmente")

print(f"\n  Antes: {engine._positions[0]}")
engine.update()
print(f"  Después: {engine._positions[0]}")
