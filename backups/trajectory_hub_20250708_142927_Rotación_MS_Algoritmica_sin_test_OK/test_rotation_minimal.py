#!/usr/bin/env python3
"""Test mínimo para diagnosticar el problema"""

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("🔍 Test Diagnóstico Mínimo")

# Crear engine
engine = EnhancedTrajectoryEngine()

# Crear una fuente
engine.create_source()
engine._positions[0] = np.array([1.0, 0.0, 0.0])

# Crear macro
engine.create_macro("test", [0])

# Aplicar rotación
success = engine.set_macro_rotation("test", speed_y=1.0)
print(f"Rotación aplicada: {success}")

# Un solo update
print("\nAntes del update:")
print(f"Posición: {engine._positions[0]}")

engine.update()

print("\nDespués del update:")
print(f"Posición: {engine._positions[0]}")

# Verificar motion_states
if hasattr(engine, 'motion_states') and 0 in engine.motion_states:
    motion = engine.motion_states[0]
    if 'macro_rotation' in motion.active_components:
        rot = motion.active_components['macro_rotation']
        print(f"\nMacroRotation:")
        print(f"  Enabled: {rot.enabled}")
        print(f"  Speed Y: {rot.speed_y}")
        print(f"  Angle Y: {rot.angle_y}")
