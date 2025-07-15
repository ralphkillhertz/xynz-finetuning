#!/usr/bin/env python3
"""
🎯 FASE 1 SIMPLIFICADA - Approach más seguro
"""

import os
import shutil
from datetime import datetime

print("=" * 80)
print("🎯 FASE 1 - APPROACH SIMPLIFICADO")
print("=" * 80)

# Primero, restaurar el archivo original
print("\n1️⃣ RESTAURANDO ARCHIVO ORIGINAL...")

motion_file = "trajectory_hub/core/motion_components.py"
backup_dirs = [
    "phase1_real_backups_20250705_161631",
    "phase1_backups_20250705_161135"
]

restored = False
for backup_dir in backup_dirs:
    backup_file = os.path.join(backup_dir, "motion_components.py")
    if os.path.exists(backup_file):
        shutil.copy2(backup_file, motion_file)
        print(f"✅ Restaurado desde: {backup_file}")
        restored = True
        break

if not restored:
    print("❌ No se encontró backup")
    exit(1)

# Crear nuevo backup
new_backup_dir = f"phase1_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(new_backup_dir, exist_ok=True)
shutil.copy2(motion_file, os.path.join(new_backup_dir, "motion_components.py"))

print("\n2️⃣ APLICANDO CAMBIOS MÍNIMOS...")

# Leer el archivo
with open(motion_file, 'r') as f:
    content = f.read()

# Agregar import al principio (si no existe)
if 'from trajectory_hub.core.compatibility_v2 import compat_v2 as compat' not in content:
    lines = content.split('\n')
    
    # Buscar dónde insertar
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('import numpy'):
            insert_idx = i + 1
            break
    
    lines.insert(insert_idx, 'from trajectory_hub.core.compatibility_v2 import compat_v2 as compat')
    content = '\n'.join(lines)
    print("✅ Import agregado")

# Ahora, encontrar y modificar SOLO la línea de interpolación
# Buscaremos el patrón exacto y lo reemplazaremos cuidadosamente

import re

# Buscar ConcentrationComponent
class_pattern = r'(class ConcentrationComponent\(MotionComponent\):.*?)(def update\(self, state: MotionState, current_time: float, dt: float\) -> MotionState:.*?)(state\.position = self\._lerp\(state\.position, target, concentration_strength\))(.*?)(?=\n    def|\nclass|\Z)'

match = re.search(class_pattern, content, re.DOTALL)

if match:
    # Extraer las partes
    before_lerp = match.group(1) + match.group(2)
    lerp_line = match.group(3)
    after_lerp = match.group(4)
    
    # Obtener la indentación correcta de la línea lerp
    # Buscar la línea en el contexto para obtener su indentación
    lines_before = (before_lerp + lerp_line).split('\n')
    lerp_line_idx = len(lines_before) - 1
    
    # Encontrar la indentación de la línea anterior no vacía
    indent = "            "  # Default: 12 espacios
    for i in range(lerp_line_idx - 1, 0, -1):
        if lines_before[i].strip():
            indent = ' ' * (len(lines_before[i]) - len(lines_before[i].lstrip()))
            break
    
    # Crear el reemplazo con la indentación correcta
    replacement = f'''if compat.is_concentration_dual_mode():
{indent}    # DUAL MODE: Calculate delta
{indent}    delta = compat.calculate_position_delta(state.position, target, concentration_strength)
{indent}    source_id = getattr(state, 'source_id', 0)
{indent}    compat.store_pending_delta(source_id, 'concentration', delta)
{indent}else:
{indent}    # ORIGINAL MODE
{indent}    state.position = self._lerp(state.position, target, concentration_strength)'''
    
    # Reemplazar
    new_content = before_lerp + indent + replacement + after_lerp
    
    # Guardar
    with open(motion_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Cambios aplicados")
    
    # Verificar sintaxis
    try:
        compile(open(motion_file).read(), motion_file, 'exec')
        print("✅ Sintaxis verificada")
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: línea {e.lineno}")
        print(f"   {e.msg}")
        
        # Mostrar contexto
        with open(motion_file, 'r') as f:
            lines = f.readlines()
        
        print("\nContexto del error:")
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 5)
        for i in range(start, end):
            marker = ">>>" if i == e.lineno - 1 else "   "
            print(f"{marker} {i+1:4d}: {lines[i]}", end='')
else:
    print("❌ No se encontró el patrón esperado")
    print("   El archivo puede tener una estructura diferente")

print("\n" + "=" * 80)
print("PRÓXIMO PASO: python test_phase1_integration.py")
print("Si falla: restaurar desde", new_backup_dir)
print("=" * 80)