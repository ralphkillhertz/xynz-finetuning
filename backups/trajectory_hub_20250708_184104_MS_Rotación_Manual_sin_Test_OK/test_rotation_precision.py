# === test_rotation_precision.py ===
# 🧪 Test de precisión de rotaciones manuales

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import math

print("🧪 TEST PRECISIÓN: Rotación Manual Mejorada")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=8, fps=60, enable_modulator=False)

# Crear macro con posiciones en cuadrado
macro_name = engine.create_macro("square", source_count=4)
macro = engine._macros[macro_name]
source_ids = list(macro.source_ids)

# Establecer posiciones en cuadrado
positions = [
    np.array([3.0, 0.0, 0.0]),   # Derecha
    np.array([0.0, 3.0, 0.0]),   # Arriba
    np.array([-3.0, 0.0, 0.0]),  # Izquierda
    np.array([0.0, -3.0, 0.0])   # Abajo
]

print("📍 Posiciones iniciales (cruz):")
for sid, pos in zip(source_ids, positions):
    engine._positions[sid] = pos
    if sid in engine.motion_states:
        engine.motion_states[sid].state.position = pos.copy()
    print(f"   Fuente {sid}: {pos}")

# Test 1: Rotación de 90 grados
print("\n🔄 Test 1: Rotación de 90 grados en Yaw")
engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi/2,  # 90 grados
    interpolation_speed=0.15  # Más rápido
)

# Más updates para asegurar convergencia
for i in range(60):
    engine.update()
    # Sincronizar states
    for sid in source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = engine._positions[sid].copy()

print("\nPosiciones después de rotar 90°:")
expected_90 = [
    np.array([0.0, 3.0, 0.0]),   # De derecha a arriba
    np.array([-3.0, 0.0, 0.0]),  # De arriba a izquierda
    np.array([0.0, -3.0, 0.0]),  # De izquierda a abajo
    np.array([3.0, 0.0, 0.0])    # De abajo a derecha
]

errors_90 = []
for sid, expected in zip(source_ids, expected_90):
    actual = engine._positions[sid]
    error = np.linalg.norm(actual - expected)
    errors_90.append(error)
    status = "✅" if error < 0.1 else "❌"
    print(f"   Fuente {sid}: [{actual[0]:.3f}, {actual[1]:.3f}, {actual[2]:.3f}] (error: {error:.3f}) {status}")

# Test 2: Rotación completa 180 grados
print("\n🔄 Test 2: Rotación completa (180 grados)")
engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi,  # 180 grados
    interpolation_speed=0.1
)

# Muchos más updates
for i in range(100):
    engine.update()
    # Sincronizar states
    for sid in source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = engine._positions[sid].copy()
    
    if i % 25 == 0:
        pos = engine._positions[source_ids[0]]
        print(f"   Update {i}: Primera fuente en [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

print("\n📊 RESULTADO FINAL:")
print("-" * 40)

expected_180 = [
    np.array([-3.0, 0.0, 0.0]),  # 180° de derecha
    np.array([0.0, -3.0, 0.0]),  # 180° de arriba
    np.array([3.0, 0.0, 0.0]),   # 180° de izquierda
    np.array([0.0, 3.0, 0.0])    # 180° de abajo
]

errors_180 = []
for sid, expected in zip(source_ids, expected_180):
    actual = engine._positions[sid]
    error = np.linalg.norm(actual - expected)
    errors_180.append(error)
    status = "✅" if error < 0.1 else "❌"
    print(f"Fuente {sid}: [{actual[0]:.3f}, {actual[1]:.3f}, {actual[2]:.3f}] (error: {error:.3f}) {status}")

# Resumen
print("\n" + "=" * 60)
avg_error_90 = np.mean(errors_90)
avg_error_180 = np.mean(errors_180)

print(f"Error promedio 90°: {avg_error_90:.3f}")
print(f"Error promedio 180°: {avg_error_180:.3f}")

if avg_error_90 < 0.1 and avg_error_180 < 0.1:
    print("\n✅ ¡ÉXITO TOTAL! Las rotaciones manuales son precisas")
elif avg_error_90 < 0.5 and avg_error_180 < 0.5:
    print("\n✅ Las rotaciones funcionan bien (error < 0.5)")
else:
    print("\n⚠️ Las rotaciones necesitan más ajuste")
