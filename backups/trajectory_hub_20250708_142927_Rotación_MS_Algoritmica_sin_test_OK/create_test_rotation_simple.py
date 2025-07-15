# === create_test_rotation_simple.py ===
# 🔧 Crear test con parámetros correctos
# ⚡ Basado en documentación del proyecto

with open("test_rotation_simple.py", "w") as f:
    f.write('''#!/usr/bin/env python3
"""Test minimalista de rotación MS - Parámetros correctos"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test Simple de Rotación MS")

# Crear engine con parámetros CORRECTOS según documentación
engine = EnhancedTrajectoryEngine(max_sources=50, fps=30)

# Crear fuentes en cuadrado
positions = [
    [2.0, 0.0, 0.0],   # Derecha
    [0.0, 2.0, 0.0],   # Arriba
    [-2.0, 0.0, 0.0],  # Izquierda
    [0.0, -2.0, 0.0]   # Abajo
]

source_names = []
for i, pos in enumerate(positions):
    name = engine.create_source(position=pos)
    source_names.append(name)
    print(f"✅ Fuente {i} creada: {name}")

# Crear macro
macro_name = engine.create_macro("test", [0, 1, 2, 3])
print(f"\\n✅ Macro creado: {macro_name}")

# Posiciones iniciales
print("\\n📍 Posiciones iniciales:")
for i in range(4):
    pos = engine._positions[i]
    print(f"  Fuente {i}: [{pos[0]:5.2f}, {pos[1]:5.2f}, {pos[2]:5.2f}]")

# Aplicar rotación
try:
    success = engine.set_macro_rotation("test", speed_y=1.0)  # 1 rad/s en Y
    print(f"\\n🔄 Rotación aplicada: {success}")
except Exception as e:
    print(f"\\n❌ Error al aplicar rotación: {e}")
    import traceback
    traceback.print_exc()

# Simular
print("\\n⏱️ Simulando 1 segundo...")
try:
    for frame in range(30):  # 1 segundo a 30 fps
        engine.update()
        if frame % 10 == 0:
            print(f"  Frame {frame}/30...")
except Exception as e:
    print(f"\\n❌ Error durante simulación: {e}")
    import traceback
    traceback.print_exc()

# Posiciones finales
print("\\n📍 Posiciones finales:")
movement_detected = False
for i in range(4):
    initial = np.array(positions[i])
    final = engine._positions[i]
    distance = np.linalg.norm(final - initial)
    
    print(f"  Fuente {i}: [{final[0]:5.2f}, {final[1]:5.2f}, {final[2]:5.2f}]")
    print(f"           Movió: {distance:.3f} unidades")
    
    if distance > 0.1:
        movement_detected = True

print(f"\\n{'✅' if movement_detected else '❌'} Resultado: {'Movimiento detectado' if movement_detected else 'Sin movimiento'}")

# Debug adicional si no hay movimiento
if not movement_detected:
    print("\\n🔍 Debug:")
    # Verificar motion states
    if hasattr(engine, 'motion_states'):
        print(f"  Motion states: {len(engine.motion_states)}")
        for sid, motion in engine.motion_states.items():
            if 'macro_rotation' in motion.active_components:
                rot = motion.active_components['macro_rotation']
                print(f"  Fuente {sid} tiene MacroRotation:")
                print(f"    Enabled: {rot.enabled}")
                print(f"    Speeds: X={rot.speed_x}, Y={rot.speed_y}, Z={rot.speed_z}")
''')

print("✅ Test creado: test_rotation_simple.py")