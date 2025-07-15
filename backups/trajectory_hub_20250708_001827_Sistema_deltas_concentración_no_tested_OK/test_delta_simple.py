#!/usr/bin/env python3
"""Test simple del sistema de deltas"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST SISTEMA DE DELTAS\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
engine.create_macro("test", [0, 1, 2])

# Posiciones iniciales
for i in range(3):
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([np.cos(angle) * 10, np.sin(angle) * 10, 0])

print("Posiciones iniciales:")
for i in range(3):
    print(f"  Source {i}: {engine._positions[i]}")

# Verificar motion_states
if hasattr(engine, 'motion_states'):
    print(f"\nMotion states: {list(engine.motion_states.keys())}")
else:
    print("\n❌ No hay motion_states")

print("\n✅ Test básico completado")
