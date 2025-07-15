#!/usr/bin/env python3
"""Test completo del sistema de deltas con debug"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST COMPLETO DEL SISTEMA DE DELTAS\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
print("1️⃣ Creando macro...")
engine.create_macro("test", [0, 1, 2])

# Verificar motion_states
print(f"\n2️⃣ Motion states creados: {list(engine.motion_states.keys())}")

# Posiciones iniciales
print("\n3️⃣ Estableciendo posiciones iniciales...")
for i in range(3):
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([np.cos(angle) * 10, np.sin(angle) * 10, 0])
    print(f"   Source {i}: {engine._positions[i]}")

# Aplicar concentración
print("\n4️⃣ Aplicando concentración...")
engine.set_macro_concentration("test", factor=0.8)

# Simular frames
print("\n5️⃣ Simulando 10 frames...")
for frame in range(10):
    positions = engine.step()
    
    if frame % 3 == 0:
        center = np.mean(positions[:3], axis=0)
        dist = np.mean([np.linalg.norm(positions[i] - center) for i in range(3)])
        print(f"   Frame {frame}: distancia promedio = {dist:.2f}")

print("\n✅ Test completado!")
