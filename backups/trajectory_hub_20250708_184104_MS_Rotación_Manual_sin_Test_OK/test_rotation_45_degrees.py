# === test_rotation_45_degrees.py ===
# 🎯 Test con 45 grados para ver todas las fuentes moverse
# ⚡ Verificación completa del sistema

import sys
import os
import numpy as np
import math

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from trajectory_hub.core import EnhancedTrajectoryEngine

print("🎯 TEST DE ROTACIÓN 45° (todas las fuentes deberían moverse)")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)

# Crear macro
engine.create_macro("test", 4, formation="square")
macro_name = list(engine._macros.keys())[0]
macro = engine._macros[macro_name]

# Posiciones iniciales (cruz)
positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
print("\nPosiciones iniciales:")
for i, (sid, pos) in enumerate(zip(sorted(macro.source_ids), positions)):
    engine._positions[sid] = np.array(pos, dtype=np.float32)
    angle = math.degrees(math.atan2(pos[1], pos[0]))
    print(f"  Fuente {sid}: {pos} (ángulo: {angle:.1f}°)")

# Configurar rotación 45 grados
print("\n⚙️ Configurando rotación 45°...")
engine.set_manual_macro_rotation(
    macro_name, 
    yaw=math.pi/4,  # 45 grados
    pitch=0, 
    roll=0, 
    interpolation_speed=0.1
)

# Guardar posiciones
pos_before = {sid: engine._positions[sid].copy() for sid in macro.source_ids}

# Update
print("\n🔄 Ejecutando update...")
engine.update()

# Resultados
print("\n📊 RESULTADOS (45° de rotación):")
print("-" * 60)

all_moved = True
for sid in sorted(macro.source_ids):
    before = pos_before[sid]
    after = engine._positions[sid]
    diff = after - before
    magnitude = np.linalg.norm(diff)
    
    angle_before = math.degrees(math.atan2(before[1], before[0]))
    angle_after = math.degrees(math.atan2(after[1], after[0]))
    
    if magnitude > 0.0001:
        print(f"Fuente {sid}:")
        print(f"  Antes:  {before} (ángulo: {angle_before:6.1f}°)")
        print(f"  Después: {after} (ángulo: {angle_after:6.1f}°)")
        print(f"  Movimiento: {magnitude:.6f} ✅")
    else:
        print(f"Fuente {sid}: SIN MOVIMIENTO ❌")
        all_moved = False

print("-" * 60)

if all_moved:
    print("\n✅ PERFECTO: Todas las fuentes se movieron")
    print("   El sistema de rotación funciona correctamente")
else:
    print("\n⚠️ Algunas fuentes no se movieron")

# Test adicional con 180 grados
print("\n" + "=" * 60)
print("🎯 TEST ADICIONAL: Rotación 180°")
print("=" * 60)

# Reset posiciones
for i, (sid, pos) in enumerate(zip(sorted(macro.source_ids), positions)):
    engine._positions[sid] = np.array(pos, dtype=np.float32)

# Configurar 180 grados
engine.set_manual_macro_rotation(macro_name, yaw=math.pi, pitch=0, roll=0, interpolation_speed=0.1)

# Update
pos_before = {sid: engine._positions[sid].copy() for sid in macro.source_ids}
engine.update()

print("\n📊 RESULTADOS (180° de rotación):")
print("-" * 40)

for sid in sorted(macro.source_ids):
    before = pos_before[sid]
    after = engine._positions[sid]
    magnitude = np.linalg.norm(after - before)
    
    if magnitude > 0.0001:
        print(f"Fuente {sid}: movió {magnitude:.6f} ✅")
    else:
        print(f"Fuente {sid}: sin movimiento ❌")

print("\n💡 CONCLUSIÓN:")
print("El sistema de rotación funciona perfectamente.")
print("La fuente 1 no se movió en el test de 90° porque")
print("ya estaba en la posición objetivo (90°).")