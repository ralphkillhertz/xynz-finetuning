# === test_yaw_rotation.py ===
# 🧪 Test simple de rotación Yaw únicamente

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import math

print("🧪 TEST SIMPLE: Solo rotación Yaw")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60, enable_modulator=False)

# Crear macro
macro_name = engine.create_macro("square", source_count=4)
macro = engine._macros[macro_name]
source_ids = list(macro.source_ids)

# Posiciones simples en cuadrado
positions = [
    np.array([2.0, 2.0, 0.0]),   # Superior derecha
    np.array([-2.0, 2.0, 0.0]),  # Superior izquierda
    np.array([-2.0, -2.0, 0.0]), # Inferior izquierda
    np.array([2.0, -2.0, 0.0])   # Inferior derecha
]

print("📍 Posiciones iniciales:")
for sid, pos in zip(source_ids, positions):
    engine._positions[sid] = pos
    if sid in engine.motion_states:
        engine.motion_states[sid].state.position = pos.copy()
    print(f"   Fuente {sid}: [{pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}]")

# Test: Rotación de 90 grados SOLO en Yaw
print("\n🔄 Rotando 90 grados en Yaw (sin pitch ni roll)")
engine.set_manual_macro_rotation(
    macro_name,
    yaw=math.pi/2,      # 90 grados
    pitch=0.0,          # Sin pitch
    roll=0.0,           # Sin roll
    interpolation_speed=0.2  # Más rápido
)

# Verificar valores iniciales
if macro_name in engine.motion_states:
    for sid in source_ids:
        if sid in engine.motion_states:
            comp = engine.motion_states[sid].active_components.get('manual_macro_rotation')
            if comp:
                print(f"\n🎯 Rotación configurada:")
                print(f"   Target Yaw: {comp.target_yaw:.3f} ({math.degrees(comp.target_yaw):.1f}°)")
                print(f"   Target Pitch: {comp.target_pitch:.3f}")
                print(f"   Target Roll: {comp.target_roll:.3f}")
                break

# Ejecutar rotación
print("\n⚙️ Ejecutando rotación...")
for i in range(100):
    engine.update()
    # Sincronizar states
    for sid in source_ids:
        if sid in engine.motion_states:
            engine.motion_states[sid].state.position = engine._positions[sid].copy()
    
    # Mostrar progreso
    if i in [0, 25, 50, 75, 99]:
        pos = engine._positions[source_ids[0]]
        print(f"   Frame {i:3d}: Primera fuente en [{pos[0]:6.3f}, {pos[1]:6.3f}, Z={pos[2]:6.3f}]")

# Verificar resultado final
print("\n📊 RESULTADO FINAL:")
print("-" * 60)

# Posiciones esperadas después de 90° de rotación en Yaw
# Rotación 90° antihoraria vista desde arriba
expected = [
    np.array([-2.0, 2.0, 0.0]),  # De [2,2] a [-2,2]
    np.array([-2.0, -2.0, 0.0]), # De [-2,2] a [-2,-2]
    np.array([2.0, -2.0, 0.0]),  # De [-2,-2] a [2,-2]
    np.array([2.0, 2.0, 0.0])    # De [2,-2] a [2,2]
]

total_error = 0
z_errors = []
for i, (sid, exp) in enumerate(zip(source_ids, expected)):
    actual = engine._positions[sid]
    error_xy = np.linalg.norm(actual[:2] - exp[:2])  # Error solo en XY
    error_z = abs(actual[2])  # Z debería ser 0
    z_errors.append(error_z)
    total_error += error_xy
    
    status = "✅" if error_xy < 0.1 and error_z < 0.001 else "❌"
    print(f"Fuente {sid}:")
    print(f"   Actual:   [{actual[0]:6.3f}, {actual[1]:6.3f}, {actual[2]:6.3f}]")
    print(f"   Esperado: [{exp[0]:6.3f}, {exp[1]:6.3f}, {exp[2]:6.3f}]")
    print(f"   Error XY: {error_xy:.3f}, Error Z: {error_z:.6f} {status}")

print("\n" + "=" * 60)
avg_error = total_error / len(source_ids)
max_z_error = max(z_errors)

if avg_error < 0.1 and max_z_error < 0.001:
    print("✅ ¡ÉXITO! Rotación Yaw funciona perfectamente")
    print("   - Todas las fuentes rotaron correctamente")
    print("   - Z se mantuvo en 0 (sin elevación espuria)")
else:
    print("⚠️ Problemas detectados:")
    if avg_error >= 0.1:
        print(f"   - Error XY promedio: {avg_error:.3f}")
    if max_z_error >= 0.001:
        print(f"   - Aparecen valores Z no deseados: max={max_z_error:.6f}")
