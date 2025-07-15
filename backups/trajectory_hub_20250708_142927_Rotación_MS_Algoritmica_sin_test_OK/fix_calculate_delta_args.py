# === fix_calculate_delta_args.py ===
# 🔧 Fix: Corregir argumentos de calculate_delta
# ⚡ Y asegurar que source_ids sea lista

import os

print("🔧 ARREGLANDO ARGUMENTOS DE calculate_delta...\n")

# 1. Arreglar motion_components.py - update_with_deltas
mc_path = "trajectory_hub/core/motion_components.py"

with open(mc_path, 'r') as f:
    content = f.read()

# Buscar update_with_deltas
if "delta = component.calculate_delta(self.state, dt)" in content:
    print("❌ update_with_deltas llama calculate_delta con argumentos incorrectos")
    
    # Corregir - necesita current_time también
    content = content.replace(
        "delta = component.calculate_delta(self.state, dt)",
        "delta = component.calculate_delta(self.state, current_time, dt)"
    )
    print("✅ Corregido a: calculate_delta(state, current_time, dt)")

# Guardar
with open(mc_path, 'w') as f:
    f.write(content)

# 2. Arreglar source_ids en EnhancedMacroSource
engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_path, 'r') as f:
    engine_content = f.read()

# Buscar EnhancedMacroSource y cambiar inicialización
if "class EnhancedMacroSource" in engine_content:
    # En el __init__
    engine_content = engine_content.replace(
        "self.source_ids = set()",
        "self.source_ids = []  # Lista, no set"
    )
    
    # En add_source
    engine_content = engine_content.replace(
        "self.source_ids.add(source_id)",
        "if source_id not in self.source_ids:\n            self.source_ids.append(source_id)"
    )
    
    print("✅ EnhancedMacroSource usa lista")

# Guardar
with open(engine_path, 'w') as f:
    f.write(engine_content)

print("\n✅ Archivos actualizados")

# TEST FINAL COMPLETO
print("\n🧪 TEST FINAL COMPLETO:")
test_code = '''
from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

print("\\n🚀 TEST MacroTrajectory COMPLETO")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
macro_id = engine.create_macro("orbita", 3)
macro = engine._macros[macro_id]

print(f"\\n✅ Macro creado: {macro_id}")
print(f"  - source_ids: {macro.source_ids} (tipo: {type(macro.source_ids).__name__})")

# Verificar componentes
ok = 0
for sid in macro.source_ids:
    if sid in engine.motion_states:
        if "macro_trajectory" in engine.motion_states[sid].active_components:
            ok += 1

print(f"  - Componentes: {ok}/{len(macro.source_ids)} fuentes con macro_trajectory")

# Configurar trayectoria
def circular(t):
    return np.array([5 * np.cos(t), 5 * np.sin(t), 0])

engine.set_macro_trajectory(macro_id, circular)
print(f"\\n✅ Trayectoria configurada")

# Test de movimiento
print("\\n🏃 Test de movimiento (2 segundos)...")
positions_before = {}
for sid in macro.source_ids:
    positions_before[sid] = engine._positions[sid].copy()

# Simular
start = time.time()
frames = 0
errors = 0

while time.time() - start < 2.0:
    try:
        engine.update()
        frames += 1
        
        if frames % 30 == 0:
            sid0 = list(macro.source_ids)[0]
            dist = np.linalg.norm(engine._positions[sid0] - positions_before[sid0])
            print(f"  Frame {frames}: distancia = {dist:.3f}")
            
    except Exception as e:
        errors += 1
        if errors == 1:
            print(f"  ❌ Error: {e}")
        if errors > 5:
            break

# Resultados
print(f"\\n📊 RESULTADOS ({frames} frames, {errors} errores):")
total_dist = 0
for sid in macro.source_ids:
    pos_after = engine._positions[sid]
    dist = np.linalg.norm(pos_after - positions_before[sid])
    total_dist += dist
    print(f"  Fuente {sid}: {dist:.3f} unidades {'✅' if dist > 0.1 else '❌'}")

avg_dist = total_dist / len(macro.source_ids)

if avg_dist > 0.1 and errors == 0:
    print(f"\\n🎉 ¡ÉXITO TOTAL! Movimiento promedio: {avg_dist:.3f}")
    print("✅ MacroTrajectory COMPLETAMENTE FUNCIONAL")
elif avg_dist > 0.1:
    print(f"\\n⚠️ PARCIAL: Movimiento {avg_dist:.3f} pero con {errors} errores")
else:
    print(f"\\n❌ FALLO: Sin movimiento significativo ({avg_dist:.6f})")
'''

# Ejecutar test
import subprocess
result = subprocess.run(['python', '-c', test_code], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    # Filtrar warnings del modulador
    errors = [line for line in result.stderr.split('\n') 
              if line and "modulador" not in line and "rotation_system" not in line]
    if errors:
        print("\nErrores:")
        for error in errors:
            print(f"  {error}")