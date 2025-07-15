#!/usr/bin/env python3
"""
🔧 FIX PRECISO DE INDENTACIÓN
"""

import os
import shutil
from datetime import datetime

print("=" * 80)
print("🔧 FIX PRECISO DE INDENTACIÓN")
print("=" * 80)

# Primero, mostrar el error actual
motion_file = "trajectory_hub/core/motion_components.py"

print("\n🔍 ANALIZANDO ERROR ACTUAL...")

with open(motion_file, 'r') as f:
    lines = f.readlines()

# Mostrar líneas con problema
print("\nContexto del error (líneas 60-70):")
for i in range(59, min(70, len(lines))):
    print(f"{i+1:4d}: '{lines[i].rstrip()}'")
    # Mostrar espacios
    spaces = len(lines[i]) - len(lines[i].lstrip())
    if lines[i].strip():
        print(f"      ^ {spaces} espacios")

# Crear backup
backup_dir = f"fix_indent_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(backup_dir, exist_ok=True)
backup_file = os.path.join(backup_dir, "motion_components.py")
shutil.copy2(motion_file, backup_file)
print(f"\n✅ Backup creado: {backup_file}")

# SOLUCIÓN: Restaurar y modificar línea por línea
print("\n🔧 APLICANDO FIX...")

# Restaurar archivo original
original_backup = "phase1_real_backups_20250705_161631/motion_components.py"
if os.path.exists(original_backup):
    with open(original_backup, 'r') as f:
        original_lines = f.readlines()
    
    # Agregar import si no existe
    import_line = 'from trajectory_hub.core.compatibility_v2 import compat_v2 as compat\n'
    import_added = False
    
    for i, line in enumerate(original_lines):
        if import_line.strip() in line:
            import_added = True
            break
    
    if not import_added:
        # Buscar dónde insertar
        for i, line in enumerate(original_lines):
            if 'import numpy as np' in line:
                original_lines.insert(i + 1, import_line)
                print("✅ Import agregado")
                break
    
    # Ahora buscar y modificar la línea específica en ConcentrationComponent
    in_concentration_component = False
    in_update_method = False
    lerp_line_found = False
    
    new_lines = []
    
    for i, line in enumerate(original_lines):
        # Detectar ConcentrationComponent
        if 'class ConcentrationComponent(MotionComponent):' in line:
            in_concentration_component = True
        elif line.strip() and not line.startswith(' ') and in_concentration_component:
            in_concentration_component = False
        
        # Detectar método update dentro de ConcentrationComponent
        if in_concentration_component and 'def update(self, state: MotionState' in line:
            in_update_method = True
        elif in_update_method and line.strip().startswith('def '):
            in_update_method = False
        
        # Buscar la línea de interpolación
        if (in_concentration_component and in_update_method and 
            'state.position = self._lerp(state.position, target, concentration_strength)' in line):
            
            # Obtener la indentación de esta línea
            indent = len(line) - len(line.lstrip())
            
            print(f"\n✅ Línea encontrada en posición {i+1}")
            print(f"   Indentación detectada: {indent} espacios")
            
            # Reemplazar con el bloque condicional
            # Usar la MISMA indentación que la línea original
            new_lines.append(f"{' ' * indent}if compat.is_concentration_dual_mode():\n")
            new_lines.append(f"{' ' * (indent + 4)}# DUAL MODE: Calculate delta\n")
            new_lines.append(f"{' ' * (indent + 4)}delta = compat.calculate_position_delta(state.position, target, concentration_strength)\n")
            new_lines.append(f"{' ' * (indent + 4)}source_id = getattr(state, 'source_id', 0)\n")
            new_lines.append(f"{' ' * (indent + 4)}compat.store_pending_delta(source_id, 'concentration', delta)\n")
            new_lines.append(f"{' ' * indent}else:\n")
            new_lines.append(f"{' ' * (indent + 4)}# ORIGINAL MODE\n")
            new_lines.append(f"{' ' * (indent + 4)}{line.strip()}\n")
            
            lerp_line_found = True
        else:
            new_lines.append(line)
    
    if lerp_line_found:
        # Escribir el archivo modificado
        with open(motion_file, 'w') as f:
            f.writelines(new_lines)
        
        print("\n✅ Archivo modificado correctamente")
        
        # Verificar sintaxis
        print("\n🧪 Verificando sintaxis...")
        try:
            compile(open(motion_file).read(), motion_file, 'exec')
            print("✅ ¡SINTAXIS CORRECTA!")
            
            # Mostrar el resultado
            print("\n📄 CAMBIO APLICADO:")
            with open(motion_file, 'r') as f:
                lines = f.readlines()
            
            # Buscar y mostrar el cambio
            for i, line in enumerate(lines):
                if 'if compat.is_concentration_dual_mode():' in line:
                    print(f"\nLíneas {i+1}-{i+9}:")
                    for j in range(i, min(i+9, len(lines))):
                        print(f"{j+1:4d}: {lines[j]}", end='')
                    break
            
        except SyntaxError as e:
            print(f"❌ Error de sintaxis: {e}")
            print("\nRestaurando backup...")
            shutil.copy2(backup_file, motion_file)
            print("✅ Backup restaurado")
    else:
        print("\n❌ No se encontró la línea de interpolación")
        print("   Restaurando archivo original...")
        shutil.copy2(original_backup, motion_file)

else:
    print("\n❌ No se encontró el backup original")

print("\n" + "=" * 80)
print("PRÓXIMO PASO: python test_phase1_integration.py")
print("=" * 80)