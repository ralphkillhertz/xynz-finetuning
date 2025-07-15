#!/usr/bin/env python3
"""Test final del sistema de deltas"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST FINAL DEL SISTEMA DE DELTAS\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Verificar motion_states
print("1️⃣ Verificando motion_states:")
print(f"   Existe: {'SÍ' if hasattr(engine, 'motion_states') else 'NO'}")

# Crear macro
source_ids = [0, 1, 2]
engine.create_macro("test", source_ids)

# Verificar que motion_states se crearon
if hasattr(engine, 'motion_states'):
    print(f"   Motion states creados: {list(engine.motion_states.keys())}")

# Posiciones iniciales
for i in source_ids:
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([np.cos(angle) * 10, np.sin(angle) * 10, 0])

print("\n2️⃣ Posiciones iniciales:")
for i in source_ids:
    print(f"   Source {i}: {engine._positions[i]}")

# Aplicar concentración
print("\n3️⃣ Aplicando concentración...")
engine.set_macro_concentration("test", factor=0.9)

# Simular
print("\n4️⃣ Simulando 20 frames...")
for frame in range(20):
    engine.step()
    
    if frame in [0, 9, 19]:
        print(f"\n   Frame {frame}:")
        center = np.mean(engine._positions[:3], axis=0)
        dist = np.mean([np.linalg.norm(engine._positions[i] - center) for i in range(3)])
        print(f"   Distancia promedio al centro: {dist:.2f}")

print("\n✅ Test completado!")
