#!/usr/bin/env python3
"""Debug ultra minimalista"""

from trajectory_hub import EnhancedTrajectoryEngine

# Crear engine y macro
engine = EnhancedTrajectoryEngine()
engine.create_macro("test", 1)  # Solo 1 fuente

print(f"Posición inicial: {engine._positions[0]}")

# Aplicar rotación
engine.set_macro_rotation("test", speed_y=1.0)

# Un update
engine.update()

print(f"Posición final: {engine._positions[0]}")

# ¿Se movió?
import numpy as np
dist = np.linalg.norm(engine._positions[0])
print(f"\nMovimiento: {'SI' if dist > 0.01 else 'NO'}")
