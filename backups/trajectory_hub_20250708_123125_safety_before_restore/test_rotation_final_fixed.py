
# Test final de rotaciones MS
import sys
sys.path.append('.')

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("\n🎯 TEST FINAL: Rotación MS Algorítmica\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=50, fps=60)
print("✅ Engine creado")

# Crear fuentes con nombres descriptivos
source_ids = []
positions = [
    [2.0, 2.0, 0.0],    # Superior derecha
    [-2.0, 2.0, 0.0],   # Superior izquierda
    [-2.0, -2.0, 0.0],  # Inferior izquierda
    [2.0, -2.0, 0.0]    # Inferior derecha
]

for i, pos in enumerate(positions):
    sid = engine.create_source(f"rotacion_{i}")
    if sid is not None:
        engine._positions[sid] = np.array(pos)
        source_ids.append(sid)
        print(f"✅ Fuente {sid} creada: rotacion_{i}")

# Crear macro
macro_name = engine.create_macro("macro_0_rotacion", source_ids[:4])
print(f"✅ Macro creado: {macro_name}")

# Aplicar rotación
print("\n🔄 Aplicando rotación...")
engine.set_macro_rotation(macro_name, speed_x=0.0, speed_y=1.0, speed_z=0.0)
print("✅ Rotación configurada")

# Simular
print("\n⏱️ Simulando 60 frames (1 segundo)...")
for frame in range(60):
    try:
        engine.update()
        if frame % 20 == 0:
            print(f"   {int((frame/60)*100)}% completado...")
    except Exception as e:
        print(f"❌ Error en frame {frame}: {e}")
        break

# Verificar movimiento
print("\n📍 Verificando movimiento:")
for i, sid in enumerate(source_ids[:4]):
    initial = np.array(positions[i])
    current = engine._positions[sid]
    distance = np.linalg.norm(current - initial)
    angle = np.arctan2(current[2] - 0, current[0] - 0) - np.arctan2(initial[2] - 0, initial[0] - 0)
    angle_deg = np.degrees(angle) % 360
    
    print(f"   Fuente {sid}: movió {distance:.2f} unidades, rotó {angle_deg:.1f}°")

print("\n✅ TEST COMPLETADO")
