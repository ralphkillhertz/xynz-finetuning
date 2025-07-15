# === test_rotation_complete.py ===
# 🎯 Test completo de rotación manual individual
# ⚡ Verificar que funciona en el sistema completo

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import math
import time

print("🎯 TEST COMPLETO DE ROTACIÓN MANUAL INDIVIDUAL")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(
    n_sources=4,
    update_rate=60,
    enable_modulator=False
)

# Configurar OSC (sin enviar realmente)
engine.osc_bridge.enabled = False

# Crear 4 fuentes en los ejes
print("1️⃣ Creando fuentes...")
positions = [
    [3.0, 0.0, 0.0],   # Eje +X
    [0.0, 3.0, 0.0],   # Eje +Y
    [-3.0, 0.0, 0.0],  # Eje -X
    [0.0, -3.0, 0.0]   # Eje -Y
]

for i, pos in enumerate(positions):
    sid = engine.create_source(i)
    engine.set_source_position(i, pos)
    print(f"   Fuente {i}: {pos}")

# Configurar rotación manual de 90° para todas
print("\n2️⃣ Configurando rotación manual de 90°...")
for i in range(4):
    success = engine.set_manual_individual_rotation(
        i,
        yaw=math.pi/2,  # 90 grados
        pitch=0.0,
        roll=0.0,
        interpolation_speed=0.1,
        center=[0.0, 0.0, 0.0]
    )
    print(f"   Fuente {i}: {'✅' if success else '❌'}")

# Verificar estados
print("\n3️⃣ Verificando componentes...")
for i in range(4):
    if i in engine.motion_states:
        motion = engine.motion_states[i]
        if hasattr(motion, 'active_components') and 'manual_individual_rotation' in motion.active_components:
            component = motion.active_components['manual_individual_rotation']
            print(f"   Fuente {i}: enabled={component.enabled}, target_yaw={math.degrees(component.target_yaw):.1f}°")

# Simular movimiento
print("\n4️⃣ Simulando rotación...")
print("-" * 80)
print("Tiempo | Fuente 0 [X,Y,Z] | Fuente 1 [X,Y,Z] | Fuente 2 [X,Y,Z] | Fuente 3 [X,Y,Z]")
print("-" * 80)

dt = 1.0 / engine.update_rate
for step in range(20):  # 20 frames
    # Update
    engine.update(dt)
    
    # Mostrar cada 5 frames
    if step % 5 == 0:
        line = f"{step*dt:5.2f}s |"
        for i in range(4):
            pos = engine._positions[i]
            line += f" [{pos[0]:5.2f},{pos[1]:5.2f},{pos[2]:5.2f}] |"
        print(line)

# Verificar resultado final
print("-" * 80)
print("\n5️⃣ RESULTADO FINAL:")
print("-" * 60)

for i in range(4):
    initial = np.array(positions[i])
    final = engine._positions[i]
    
    # Calcular ángulo de rotación
    initial_angle = math.atan2(initial[1], initial[0])
    final_angle = math.atan2(final[1], final[0])
    rotation = math.degrees(final_angle - initial_angle)
    
    # Radio
    initial_radius = np.linalg.norm(initial[:2])
    final_radius = np.linalg.norm(final[:2])
    
    print(f"Fuente {i}:")
    print(f"   Inicial: {initial} (ángulo: {math.degrees(initial_angle):.1f}°)")
    print(f"   Final:   {final} (ángulo: {math.degrees(final_angle):.1f}°)")
    print(f"   Rotación: {rotation:.1f}°")
    print(f"   Radio: {initial_radius:.3f} → {final_radius:.3f}")
    print()

# Test del sistema de deltas
print("6️⃣ Verificando sistema de deltas...")
if hasattr(engine, 'motion_states'):
    for i in range(4):
        if i in engine.motion_states:
            motion = engine.motion_states[i]
            if hasattr(motion, 'state'):
                print(f"   Fuente {i}: state.position = {motion.state.position}")

print("\n✅ Test completado")