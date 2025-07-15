# === test_rotation_final.py ===
# Test definitivo de rotaciones

import sys
import os
import numpy as np
import math

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from trajectory_hub.core import EnhancedTrajectoryEngine

print("🎯 TEST FINAL DE ROTACIÓN")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)

# Crear macro
engine.create_macro("test", 4, formation="square")
macro_name = list(engine._macros.keys())[0]
macro = engine._macros[macro_name]

print(f"✅ Macro creado: {macro_name}")
print(f"   Fuentes: {macro.source_ids}")

# Establecer posiciones
positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
for i, (sid, pos) in enumerate(zip(sorted(macro.source_ids), positions)):
    engine._positions[sid] = np.array(pos, dtype=np.float32)
    print(f"   Fuente {sid}: {pos}")

# Configurar rotación 90 grados
print("\n⚙️ Configurando rotación 90°...")
engine.set_manual_macro_rotation(
    macro_name, 
    yaw=math.pi/2,  # 90 grados
    pitch=0, 
    roll=0, 
    interpolation_speed=0.1
)

# Guardar posiciones iniciales
pos_before = {}
for sid in macro.source_ids:
    pos_before[sid] = engine._positions[sid].copy()

# Ejecutar update
print("\n🔄 Ejecutando engine.update()...")
engine.update()

# Verificar cambios
print("\n📊 RESULTADOS:")
print("-" * 40)

total_movement = 0
for sid in sorted(macro.source_ids):
    before = pos_before[sid]
    after = engine._positions[sid]
    diff = after - before
    magnitude = np.linalg.norm(diff)
    total_movement += magnitude
    
    if magnitude > 0.0001:
        print(f"Fuente {sid}: {before} → {after}")
        print(f"           Movimiento: {diff} (magnitud: {magnitude:.6f}) ✅")
    else:
        print(f"Fuente {sid}: Sin cambios ❌")

print("-" * 40)

if total_movement > 0.0001:
    print(f"\n✅ ¡ÉXITO! Las rotaciones funcionan")
    print(f"   Movimiento total: {total_movement:.6f}")
else:
    print("\n❌ Las rotaciones NO funcionan")
