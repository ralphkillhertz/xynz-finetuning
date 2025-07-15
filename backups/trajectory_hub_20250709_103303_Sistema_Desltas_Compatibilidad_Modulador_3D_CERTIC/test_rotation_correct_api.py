# === test_rotation_correct_api.py ===
# 🎯 Test con API correcta
# ⚡ Usando max_sources y fps

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import math

print("🎯 TEST ROTACIÓN MANUAL INDIVIDUAL - API CORRECTA")
print("=" * 60)

# Crear engine con parámetros correctos
engine = EnhancedTrajectoryEngine(
    max_sources=10,
    fps=60
)

# Deshabilitar OSC
engine.osc_bridge.enabled = False

# Crear una fuente simple
print("1️⃣ Creando fuente en posición [3, 0, 0]...")
sid = engine.create_source(0)
engine.set_source_position(0, [3.0, 0.0, 0.0])

# Configurar rotación manual
print("\n2️⃣ Configurando rotación manual 90°...")
success = engine.set_manual_individual_rotation(
    0,
    yaw=math.pi/2,  # 90 grados
    pitch=0.0,
    roll=0.0,
    interpolation_speed=0.1,
    center=[0.0, 0.0, 0.0]
)
print(f"   Configuración: {'✅ Exitosa' if success else '❌ Falló'}")

# Verificar componente
if 0 in engine.motion_states:
    motion = engine.motion_states[0]
    if hasattr(motion, 'active_components') and 'manual_individual_rotation' in motion.active_components:
        comp = motion.active_components['manual_individual_rotation']
        print(f"   Componente activo: enabled={comp.enabled}")
        print(f"   Target yaw: {math.degrees(comp.target_yaw):.1f}°")

# Simular rotación
print("\n3️⃣ Simulando rotación (2 segundos)...")
print("-" * 60)
print("Tiempo |  Posición [X, Y, Z]  | Ángulo  | Radio")
print("-" * 60)

dt = 1.0 / 60  # 60 FPS
steps = 120    # 2 segundos

for step in range(0, steps + 1, 20):  # Cada 20 frames
    # Update engine
    for _ in range(min(20, steps - step)):
        engine.update(dt)
    
    # Obtener posición
    pos = engine._positions[0]
    angle = math.degrees(math.atan2(pos[1], pos[0]))
    radius = np.linalg.norm(pos[:2])
    
    print(f"{step*dt:5.2f}s | [{pos[0]:6.3f}, {pos[1]:6.3f}, {pos[2]:6.3f}] | {angle:6.1f}° | {radius:6.3f}")

# Resultado final
print("-" * 60)
pos_final = engine._positions[0]
angle_final = math.degrees(math.atan2(pos_final[1], pos_final[0]))

print(f"\n📊 RESULTADO FINAL:")
print(f"   Posición inicial: [3.000, 0.000, 0.000] (0°)")
print(f"   Posición final:   [{pos_final[0]:.3f}, {pos_final[1]:.3f}, {pos_final[2]:.3f}] ({angle_final:.1f}°)")
print(f"   Rotación lograda: {angle_final:.1f}°")
print(f"   Radio mantenido:  {np.linalg.norm(pos_final[:2]):.3f}")

if abs(angle_final - 90.0) < 5.0:
    print("\n✅ ¡ROTACIÓN EXITOSA!")
else:
    print(f"\n⚠️ Rotación incompleta (esperado 90°, obtenido {angle_final:.1f}°)")

print("\n✅ Test completado")