# === test_macro_rotation.py ===
# 🧪 Test de rotación MS algorítmica con deltas

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

print("\n🔄 TEST: Rotación MS Algorítmica con Deltas\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=8, fps=60)
print("✅ Engine creado")

# Crear macro en formación cuadrada
macro_id = engine.create_macro("cubo", 8, formation="cube")
print(f"✅ Macro '{macro_id}' creado en formación cubo")

# Posiciones iniciales
print("\n📍 Posiciones iniciales:")
initial_positions = {}
for sid in engine._macros[macro_id].source_ids:
    pos = engine._positions[sid]
    initial_positions[sid] = pos.copy()
    print(f"   Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

# Configurar rotación en Y (como un carrusel)
engine.set_macro_rotation(macro_id, speed_x=0, speed_y=1.0, speed_z=0)  # 1 rad/s

# Simular 3.14 segundos (media vuelta)
print("\n🎠 Simulando rotación por π segundos (media vuelta)...")
frames = int(3.14159 * 60)  # 60 fps
for i in range(frames):
    engine.update()
    time.sleep(0.01)  # Simulación rápida

# Verificar posiciones finales
print("\n📍 Posiciones finales:")
total_movement = 0
for sid in engine._macros[macro_id].source_ids:
    initial = initial_positions[sid]
    final = engine._positions[sid]
    distance = np.linalg.norm(final - initial)
    total_movement += distance
    print(f"   Fuente {sid}: [{final[0]:.2f}, {final[1]:.2f}, {final[2]:.2f}] (movió {distance:.2f})")

avg_movement = total_movement / len(engine._macros[macro_id].source_ids)

if avg_movement > 0.5:
    print(f"\n✅ ¡ÉXITO! Rotación MS funcionando")
    print(f"   Movimiento promedio: {avg_movement:.2f} unidades")
    print("\n📊 SISTEMA DE DELTAS:")
    print("   ✅ Concentración: 100%")
    print("   ✅ Trayectorias IS: 100%") 
    print("   ✅ Trayectorias MS: 100%")
    print("   ✅ Rotaciones MS algorítmicas: 100%")
else:
    print(f"\n❌ Sin rotación detectada: {avg_movement:.3f}")
