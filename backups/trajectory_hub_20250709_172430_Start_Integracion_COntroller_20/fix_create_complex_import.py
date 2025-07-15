#!/usr/bin/env python3
"""
🔧 Fix: Quitar import inexistente create_complex_movement
⚡ Limpia imports de motion_components
"""

import os

# Leer archivo
with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'r') as f:
    lines = f.readlines()

# Buscar y arreglar el bloque de imports
in_import_block = False
fixed_lines = []

for line in lines:
    if "from trajectory_hub.core.motion_components import" in line:
        in_import_block = True
        fixed_lines.append(line)
    elif in_import_block:
        # Quitar create_complex_movement
        if "create_complex_movement" in line:
            # Eliminar create_complex_movement y la coma
            line = line.replace("create_complex_movement, ", "")
            line = line.replace(", create_complex_movement", "")
            line = line.replace("create_complex_movement,", "")
            print("✅ Eliminado import create_complex_movement")
        
        fixed_lines.append(line)
        
        if ")" in line and not line.strip().startswith("from"):
            in_import_block = False
    else:
        fixed_lines.append(line)

# Guardar
with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'w') as f:
    f.writelines(fixed_lines)

print("✅ Imports corregidos")

# Verificar otros imports problemáticos
print("\n🔍 Verificando imports...")
import_line = ""
for line in fixed_lines:
    if "from trajectory_hub.core.motion_components import" in line:
        import_line = line
    elif import_line and ")" in line:
        print(f"  Imports actuales: {import_line.strip()} ... {line.strip()}")
        break