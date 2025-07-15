# === test_rotation_fixed.py ===
# Test para verificar que las rotaciones funcionan

import sys
import os
import numpy as np
import math

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from trajectory_hub.core import EnhancedTrajectoryEngine

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)

# Crear macro
engine.create_macro("test", 4, formation="square")
macro_name = list(engine._macros.keys())[0]

# Posiciones iniciales
positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
macro = engine._macros[macro_name]

for i, (sid, pos) in enumerate(zip(macro.source_ids, positions)):
    engine._positions[sid] = np.array(pos, dtype=np.float32)

# Configurar rotación
engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2, pitch=0, roll=0, interpolation_speed=0.1)

# Guardar posiciones iniciales
pos_before = {sid: engine._positions[sid].copy() for sid in macro.source_ids}

# Update
engine.update()

# Verificar cambios
print("🎯 TEST DE ROTACIÓN:")
print("-" * 40)
any_change = False
for sid in macro.source_ids:
    before = pos_before[sid]
    after = engine._positions[sid]
    diff = np.linalg.norm(after - before)
    
    if diff > 0.0001:
        print(f"Fuente {sid}: {before} → {after} ✅")
        any_change = True
    else:
        print(f"Fuente {sid}: Sin cambios ❌")

if any_change:
    print("\n✅ ¡ROTACIÓN FUNCIONA!")
else:
    print("\n❌ Rotación sigue sin funcionar")
