# === test_individual_rotations.py ===
# 🎯 Test completo de rotaciones individuales (IS)
# ⚡ Verifica IndividualRotation y ManualIndividualRotation

import sys
import os
import numpy as np
import math
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from trajectory_hub.core import EnhancedTrajectoryEngine

print("🎯 TEST DE ROTACIONES INDIVIDUALES (IS)")
print("=" * 60)

# Crear engine
print("\n1️⃣ Creando engine...")
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)

# Crear fuentes individuales
print("\n2️⃣ Creando fuentes individuales...")
source_ids = []
for i in range(4):
    motion = engine.create_source(i)
    source_ids.append(i)

# Establecer posiciones iniciales
positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
for sid, pos in zip(source_ids, positions):
    engine._positions[sid] = np.array(pos, dtype=np.float32)
    print(f"   Fuente {sid}: {pos}")

# TEST 1: Rotación algorítmica individual
print("\n" + "="*60)
print("📋 TEST 1: ROTACIÓN ALGORÍTMICA INDIVIDUAL")
print("="*60)

# Configurar rotación algorítmica para fuente 0
print("\nConfigurando rotación algorítmica para fuente 0...")
engine.set_individual_rotation(0, speed_y=1.0)  # 1 rad/s en Y

# Guardar posición inicial
pos_before = engine._positions[0].copy()

# Ejecutar varios updates
print("\nEjecutando 5 updates...")
for i in range(5):
    engine.update()
    pos_after = engine._positions[0]
    movement = np.linalg.norm(pos_after - pos_before)
    print(f"   Update {i+1}: Posición {pos_after}, movimiento: {movement:.6f}")
    pos_before = pos_after.copy()

# Verificar
if movement > 0.001:
    print("✅ Rotación algorítmica funciona")
else:
    print("❌ Rotación algorítmica NO funciona")

# TEST 2: Rotación manual individual
print("\n" + "="*60)
print("📋 TEST 2: ROTACIÓN MANUAL INDIVIDUAL")
print("="*60)

# Reset posición
engine._positions[1] = np.array([0, 3, 0], dtype=np.float32)

# Configurar rotación manual
print("\nConfigurando rotación manual para fuente 1 (45°)...")
engine.set_manual_individual_rotation(1, yaw=math.pi/4, interpolation_speed=0.1)

# Guardar posición inicial
pos_before = engine._positions[1].copy()

# Ejecutar updates
print("\nEjecutando 5 updates...")
total_movement = 0
for i in range(5):
    engine.update()
    pos_after = engine._positions[1]
    movement = np.linalg.norm(pos_after - pos_before)
    total_movement += movement
    if movement > 0.001:
        print(f"   Update {i+1}: Movimiento {movement:.6f} ✅")
    pos_before = pos_after.copy()

if total_movement > 0.001:
    print("✅ Rotación manual funciona")
else:
    print("❌ Rotación manual NO funciona")

# TEST 3: Batch rotation con desfase
print("\n" + "="*60)
print("📋 TEST 3: BATCH ROTATION CON DESFASE")
print("="*60)

# Configurar todas las fuentes con desfase
print("\nConfigurando rotación batch con desfase...")
engine.set_batch_individual_rotation(source_ids, speed_y=0.5, offset_factor=0.2)

# Ejecutar y verificar
print("\nEjecutando 10 updates...")
movements = {sid: 0.0 for sid in source_ids}
pos_before = {sid: engine._positions[sid].copy() for sid in source_ids}

for _ in range(10):
    engine.update()
    for sid in source_ids:
        movement = np.linalg.norm(engine._positions[sid] - pos_before[sid])
        movements[sid] += movement
        pos_before[sid] = engine._positions[sid].copy()

print("\nMovimientos totales:")
all_moved = True
for sid, total in movements.items():
    status = "✅" if total > 0.001 else "❌"
    print(f"   Fuente {sid}: {total:.6f} {status}")
    if total < 0.001:
        all_moved = False

if all_moved:
    print("✅ Batch rotation funciona")
else:
    print("❌ Batch rotation tiene problemas")

# TEST 4: Stop rotation
print("\n" + "="*60)
print("📋 TEST 4: DETENER ROTACIONES")
print("="*60)

# Detener rotación de fuente 0
print("\nDeteniendo rotación de fuente 0...")
engine.stop_individual_rotation(0)

# Verificar que no se mueve
pos_before = engine._positions[0].copy()
engine.update()
engine.update()
pos_after = engine._positions[0]
movement = np.linalg.norm(pos_after - pos_before)

if movement < 0.001:
    print("✅ Stop rotation funciona")
else:
    print("❌ Stop rotation NO funciona")

# RESUMEN FINAL
print("\n" + "="*60)
print("📊 RESUMEN DE TESTS")
print("="*60)

tests_passed = 0
total_tests = 4

# Verificar cada test
if movements[0] > 0.001:
    tests_passed += 1
    print("✅ TEST 1: Rotación algorítmica - PASADO")
else:
    print("❌ TEST 1: Rotación algorítmica - FALLADO")

if total_movement > 0.001:
    tests_passed += 1
    print("✅ TEST 2: Rotación manual - PASADO")
else:
    print("❌ TEST 2: Rotación manual - FALLADO")

if all_moved:
    tests_passed += 1
    print("✅ TEST 3: Batch rotation - PASADO")
else:
    print("❌ TEST 3: Batch rotation - FALLADO")

if movement < 0.001:
    tests_passed += 1
    print("✅ TEST 4: Stop rotation - PASADO")
else:
    print("❌ TEST 4: Stop rotation - FALLADO")

print(f"\nTotal: {tests_passed}/{total_tests} tests pasados")

if tests_passed == total_tests:
    print("\n🎉 ¡TODAS LAS ROTACIONES IS FUNCIONAN PERFECTAMENTE! 🎉")
else:
    print(f"\n⚠️ Hay {total_tests - tests_passed} tests que fallan")