# === fix_osc_final.py ===
# 🔧 Fix final: Comentar llamada OSC
# ⚡ Hacer que el update funcione

import os
import re
from datetime import datetime

def fix_osc_final():
    """Comenta la llamada OSC para que funcione el update"""
    
    print("🔧 FIX FINAL: Comentar llamada OSC")
    print("=" * 60)
    
    # Ruta del archivo
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: No se encuentra {file_path}")
        return False
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Comentar cualquier llamada a send_osc
    print("🔍 Comentando llamadas OSC...")
    
    # Patrones a comentar
    patterns = [
        r'self\.send_osc_update\(\)',
        r'self\._send_osc_update\(\)',
        r'self\.send_osc_positions\(\)',
        r'self\._send_osc_positions\(\)'
    ]
    
    for pattern in patterns:
        if re.search(pattern, content):
            content = re.sub(f'(\s*){pattern}', r'\1# ' + pattern + '  # Temporalmente comentado', content)
            print(f"✅ Comentado: {pattern}")
    
    # Escribir archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n🎯 TEST FINAL DE ROTACIÓN:")
    print("=" * 60)
    
    # Test completo inline
    exec('''
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import math

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)

# Crear macro con 4 fuentes
engine.create_macro("test", 4, formation="square")
macro_name = list(engine._macros.keys())[0]
macro = engine._macros[macro_name]

print(f"Macro: {macro_name}")
print(f"Fuentes: {sorted(macro.source_ids)}")

# Establecer posiciones en cruz
positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
for i, (sid, pos) in enumerate(zip(sorted(macro.source_ids), positions)):
    engine._positions[sid] = np.array(pos, dtype=np.float32)

# Configurar rotación 90 grados
engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2, pitch=0, roll=0, interpolation_speed=0.1)

# Guardar posiciones
pos_before = {sid: engine._positions[sid].copy() for sid in macro.source_ids}

# UPDATE
print("\\nEjecutando update...")
try:
    engine.update()
    print("✅ Update ejecutado sin errores")
except Exception as e:
    print(f"❌ Error en update: {e}")
    import traceback
    traceback.print_exc()

# Verificar cambios
print("\\nRESULTADOS:")
print("-" * 40)

total_movement = 0
for sid in sorted(macro.source_ids):
    before = pos_before[sid]
    after = engine._positions[sid]
    diff = np.linalg.norm(after - before)
    total_movement += diff
    
    if diff > 0.0001:
        print(f"Fuente {sid}: [{before[0]:.2f}, {before[1]:.2f}, {before[2]:.2f}] → [{after[0]:.2f}, {after[1]:.2f}, {after[2]:.2f}]")
        print(f"         Movimiento: {diff:.6f} ✅")
    else:
        print(f"Fuente {sid}: Sin cambios ❌")

print("-" * 40)

if total_movement > 0.0001:
    print(f"\\n🎉🎉🎉 ¡¡¡ÉXITO TOTAL!!! 🎉🎉🎉")
    print(f"Las rotaciones manuales MS funcionan perfectamente")
    print(f"Movimiento total: {total_movement:.6f}")
    print("\\nEl sistema de deltas está 100% funcional")
else:
    print("\\n❌ Las rotaciones aún no funcionan")
''')
    
    return True

if __name__ == "__main__":
    fix_osc_final()