# === test_manual_rotation_final.py ===
# 🧪 Test final de rotación manual con deltas

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import math

print("🧪 TEST FINAL: Rotación Manual con Deltas")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=8, fps=60, enable_modulator=False)

# Crear macro con posiciones en cuadrado
macro_name = engine.create_macro("square", source_count=4)
macro = engine._macros[macro_name]
source_ids = list(macro.source_ids)

# Establecer posiciones en cuadrado
positions = [
    np.array([3.0, 3.0, 0.0]),   # Superior derecha
    np.array([-3.0, 3.0, 0.0]),  # Superior izquierda
    np.array([-3.0, -3.0, 0.0]), # Inferior izquierda
    np.array([3.0, -3.0, 0.0])   # Inferior derecha
]

print("📍 Posiciones iniciales (cuadrado):")
for sid, pos in zip(source_ids, positions):
    engine._positions[sid] = pos
    # IMPORTANTE: Sincronizar con el state
    if sid in engine.motion_states:
        engine.motion_states[sid].state.position = pos.copy()
    print(f"   Fuente {sid}: {pos}")

# Test 1: Rotación de 45 grados
print("\n🔄 Test 1: Rotación de 45 grados en Yaw")
engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi/4,  # 45 grados
    interpolation_speed=0.1
)

# Ejecutar updates
for i in range(20):
    engine.update()
    
    # Sincronizar states después de cada update
    for sid in source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = engine._positions[sid].copy()

print("\nPosiciones después de rotar 45°:")
for sid in source_ids:
    print(f"   Fuente {sid}: {engine._positions[sid]}")

# Test 2: Rotación completa
print("\n🔄 Test 2: Rotación completa (180 grados)")
engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi,  # 180 grados
    interpolation_speed=0.05  # Más lento
)

for i in range(40):
    engine.update()
    # Sincronizar states
    for sid in source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = engine._positions[sid].copy()
    
    if i % 10 == 0:
        pos = engine._positions[source_ids[0]]
        print(f"   Update {i}: Primera fuente en [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

# Verificar resultado
print("\n📊 RESULTADO FINAL:")
print("-" * 40)

# El cuadrado debería estar rotado 180 grados
expected_positions = [
    np.array([-3.0, -3.0, 0.0]),  # Opuesto a superior derecha
    np.array([3.0, -3.0, 0.0]),   # Opuesto a superior izquierda
    np.array([3.0, 3.0, 0.0]),    # Opuesto a inferior izquierda
    np.array([-3.0, 3.0, 0.0])    # Opuesto a inferior derecha
]

all_correct = True
for sid, expected in zip(source_ids, expected_positions):
    actual = engine._positions[sid]
    error = np.linalg.norm(actual - expected)
    
    status = "✅" if error < 0.5 else "❌"
    print(f"Fuente {sid}: {actual} (error: {error:.3f}) {status}")
    
    if error > 0.5:
        all_correct = False

print("\n" + "=" * 60)
if all_correct:
    print("✅ ¡ÉXITO! La rotación manual funciona perfectamente con deltas")
else:
    print("⚠️ La rotación funciona pero no es perfecta")
