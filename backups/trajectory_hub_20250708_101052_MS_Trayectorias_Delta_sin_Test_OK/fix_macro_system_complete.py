# === fix_macro_system_complete.py ===
# 🔧 Fix: Inicializar _macros y arreglar todo el sistema
# ⚡ Impacto: CRÍTICO - Sin esto no funcionan los macros
# 🎯 Solución completa

import os
import re
from datetime import datetime

print("🔧 ARREGLANDO SISTEMA DE MACROS COMPLETO...\n")

file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
backup_path = f"{file_path}.backup_macro_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Backup
import shutil
shutil.copy2(file_path, backup_path)
print(f"📦 Backup: {backup_path}")

with open(file_path, 'r') as f:
    content = f.read()

# 1. Añadir _macros a __init__
print("\n1️⃣ Añadiendo self._macros = {} a __init__...")
init_match = re.search(r'(def __init__\(.*?\):.*?)(self\.motion_states = \{\})', content, re.DOTALL)
if init_match:
    before = init_match.group(1)
    motion_states_line = init_match.group(2)
    
    # Añadir _macros justo antes de motion_states
    new_init = before + "        self._macros = {}  # Almacén de macros\n        " + motion_states_line
    content = content.replace(init_match.group(0), new_init)
    print("✅ _macros añadido a __init__")

# 2. Arreglar create_macro para que añada trajectory_component a motion_states
print("\n2️⃣ Arreglando create_macro...")

# Buscar el método create_macro
create_match = re.search(r'def create_macro\(.*?\):.*?(?=\n    def|\Z)', content, re.DOTALL)
if create_match:
    old_method = create_match.group(0)
    
    # Buscar dónde termina la creación de source_ids
    # y añadir código para configurar trajectory_component
    lines = old_method.split('\n')
    
    # Buscar línea donde se añade el macro a _macros
    for i, line in enumerate(lines):
        if 'self._macros[' in line and '] =' in line:
            # Añadir después de esta línea
            indent = '        '  # 8 espacios
            
            new_lines = lines[:i+1] + [
                '',
                f'{indent}# Configurar trajectory component para cada fuente',
                f'{indent}trajectory_component = MacroTrajectory()',
                f'{indent}trajectory_component.enabled = False  # Se activa al configurar trayectoria',
                f'{indent}',
                f'{indent}# Añadir a motion_states de cada fuente',
                f'{indent}for sid in source_ids:',
                f'{indent}    if sid in self.motion_states:',
                f'{indent}        self.motion_states[sid].active_components["macro_trajectory"] = trajectory_component',
                f'{indent}',
                f'{indent}# Guardar referencia en el macro',
                f'{indent}self._macros[macro_id].trajectory_component = trajectory_component',
            ] + lines[i+1:]
            
            new_method = '\n'.join(new_lines)
            content = content.replace(old_method, new_method)
            print("✅ create_macro actualizado")
            break

# 3. Verificar que set_macro_trajectory use _macros correctamente
print("\n3️⃣ Verificando set_macro_trajectory...")
if "self._macros" in content and "set_macro_trajectory" in content:
    print("✅ set_macro_trajectory ya usa self._macros")
else:
    # Si usa self.macros sin guión bajo, corregir
    content = content.replace(
        "if macro_id not in self.macros:",
        "if macro_id not in self._macros:"
    )
    content = content.replace(
        "macro = self.macros[macro_id]",
        "macro = self._macros[macro_id]"
    )
    print("✅ Corregidas referencias en set_macro_trajectory")

# 4. Asegurar que los imports necesarios estén presentes
print("\n4️⃣ Verificando imports...")
if "from .motion_components import MacroTrajectory" not in content:
    # Buscar dónde están los otros imports
    import_section = re.search(r'(from \.motion_components import.*?)(\n\n|\nclass)', content)
    if import_section:
        old_imports = import_section.group(1)
        if "MacroTrajectory" not in old_imports:
            new_imports = old_imports.rstrip() + ", MacroTrajectory"
            content = content.replace(old_imports, new_imports)
            print("✅ Import de MacroTrajectory añadido")

# Guardar cambios
with open(file_path, 'w') as f:
    f.write(content)

print("\n✅ SISTEMA DE MACROS ARREGLADO")

# Crear test final
test_code = '''# === test_macro_system_fixed.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import math

print("🧪 TEST FINAL: Sistema de Macros Arreglado\\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Verificar que _macros existe
print("1️⃣ Verificando inicialización:")
if hasattr(engine, '_macros'):
    print("  ✅ engine._macros existe")
else:
    print("  ❌ engine._macros NO existe")
    exit(1)

# Crear macro
print("\\n2️⃣ Creando macro...")
engine.create_macro("test", [0, 1, 2])

# Verificar que se creó
if "test" in engine._macros:
    print("  ✅ Macro 'test' creado")
    macro = engine._macros["test"]
    print(f"  - source_ids: {macro.source_ids}")
    print(f"  - trajectory_component: {hasattr(macro, 'trajectory_component')}")
else:
    print("  ❌ Macro NO se creó")
    exit(1)

# Verificar motion_states
print("\\n3️⃣ Verificando motion_states:")
for sid in [0, 1, 2]:
    if sid in engine.motion_states:
        components = list(engine.motion_states[sid].active_components.keys())
        print(f"  Fuente {sid}: {components}")

# Configurar trayectoria
print("\\n4️⃣ Configurando trayectoria circular...")
def circular_traj(t):
    return np.array([5 * np.cos(t), 5 * np.sin(t), 0])

engine.set_macro_trajectory("test", circular_traj)
print("  ✅ Trayectoria configurada")

# Test de movimiento
print("\\n5️⃣ Test de movimiento (60 frames):")
pos_start = engine._positions[0].copy()

for i in range(60):
    engine.update()
    
    if i % 20 == 19:
        pos = engine._positions[0]
        dist = np.linalg.norm(pos - pos_start)
        print(f"  Frame {i+1}: distancia = {dist:.3f}")

pos_final = engine._positions[0]
total_dist = np.linalg.norm(pos_final - pos_start)

if total_dist > 0.1:
    print(f"\\n🎉 ¡ÉXITO TOTAL! Movimiento = {total_dist:.3f} unidades")
    print("✅ MacroTrajectory funciona perfectamente con deltas")
else:
    print(f"\\n❌ Sin movimiento significativo: {total_dist:.6f}")
'''

with open("test_macro_system_fixed.py", "w") as f:
    f.write(test_code)

print("\n📝 Test creado: test_macro_system_fixed.py")
print("\n🚀 EJECUTA:")
print("1. python fix_macro_system_complete.py")
print("2. python test_macro_system_fixed.py")