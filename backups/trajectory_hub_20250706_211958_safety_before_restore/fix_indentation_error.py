#!/usr/bin/env python3
"""
🔧 FIX DE INDENTACIÓN EN motion_components.py
"""

import os
import shutil
from datetime import datetime

print("=" * 80)
print("🔧 CORRIGIENDO ERROR DE INDENTACIÓN")
print("=" * 80)

# Leer el archivo con error
motion_file = "trajectory_hub/core/motion_components.py"

# Hacer backup del archivo con error
error_backup = f"motion_components_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
shutil.copy2(motion_file, error_backup)
print(f"✅ Backup del archivo con error: {error_backup}")

# Leer contenido
with open(motion_file, 'r') as f:
    lines = f.readlines()

print(f"\n🔍 Buscando línea con error (línea 1031)...")

# Mostrar contexto del error
if len(lines) >= 1031:
    print("\nContexto del error:")
    for i in range(max(0, 1025), min(len(lines), 1035)):
        print(f"{i+1:4d}: {lines[i]}", end='')

# Buscar el patrón problemático y corregir indentación
fixed_lines = []
in_concentration_update = False
base_indent = None
concentration_line = -1

for i, line in enumerate(lines):
    # Detectar cuando entramos en el método update de ConcentrationComponent
    if 'def update(self, state: MotionState' in line and in_concentration_update == False:
        # Verificar si estamos en ConcentrationComponent mirando hacia atrás
        for j in range(max(0, i-50), i):
            if 'class ConcentrationComponent' in lines[j]:
                in_concentration_update = True
                base_indent = len(line) - len(line.lstrip())
                print(f"\n✅ Encontrado update de ConcentrationComponent en línea {i+1}")
                print(f"   Indentación base del método: {base_indent} espacios")
                break
    
    # Si estamos en el método update de ConcentrationComponent
    if in_concentration_update:
        # Detectar el final del método
        if line.strip() and not line.startswith(' ' * base_indent) and i > concentration_line + 10:
            in_concentration_update = False
        
        # Buscar la línea problemática
        if 'if compat.is_concentration_dual_mode():' in line:
            concentration_line = i
            # Calcular la indentación correcta
            # Debe estar al mismo nivel que otras declaraciones en el método
            correct_indent = base_indent + 8  # 8 espacios dentro del método
            
            # Buscar la indentación del contexto anterior
            for j in range(i-1, max(0, i-10), -1):
                if lines[j].strip() and 'concentration_strength' in lines[j]:
                    # Usar la misma indentación que concentration_strength
                    correct_indent = len(lines[j]) - len(lines[j].lstrip())
                    print(f"\n🔧 Corrigiendo indentación en línea {i+1}")
                    print(f"   Indentación actual: {len(line) - len(line.lstrip())}")
                    print(f"   Indentación correcta: {correct_indent}")
                    break
            
            # Aplicar indentación correcta a esta línea y las siguientes del bloque
            line = ' ' * correct_indent + line.lstrip()
        
        # Si estamos en el bloque del if compat... corregir las siguientes líneas también
        elif concentration_line > 0 and i > concentration_line and i < concentration_line + 20:
            if line.strip():  # Si la línea no está vacía
                # Determinar la indentación correcta basándose en el contenido
                if line.strip().startswith('else:'):
                    # else debe estar al mismo nivel que if
                    line = ' ' * (base_indent + 8) + line.lstrip()
                elif 'DUAL MODE:' in line or 'ORIGINAL MODE:' in line:
                    # Comentarios dentro del if/else
                    line = ' ' * (base_indent + 12) + line.lstrip()
                elif line.strip().startswith('#'):
                    # Otros comentarios
                    if i < concentration_line + 10:
                        line = ' ' * (base_indent + 12) + line.lstrip()
                    else:
                        line = ' ' * (base_indent + 12) + line.lstrip()
                else:
                    # Código dentro del if/else
                    if 'state.position = self._lerp' in line:
                        # Esta línea debe estar dentro del else
                        line = ' ' * (base_indent + 12) + line.lstrip()
                    else:
                        # Otras líneas de código
                        line = ' ' * (base_indent + 12) + line.lstrip()
    
    fixed_lines.append(line)

# Escribir archivo corregido
with open(motion_file, 'w') as f:
    f.writelines(fixed_lines)

print("\n✅ Indentación corregida")

# Verificar que el archivo es válido Python
print("\n🧪 Verificando sintaxis...")
try:
    compile(open(motion_file).read(), motion_file, 'exec')
    print("✅ Sintaxis correcta")
except SyntaxError as e:
    print(f"❌ Error de sintaxis en línea {e.lineno}: {e.msg}")
    print("\n⚠️ Restaurando backup...")
    
    # Buscar el backup más reciente que funcione
    backup_found = False
    for backup_dir in ["phase1_real_backups_20250705_161631", "phase1_backups_20250705_161135"]:
        backup_file = os.path.join(backup_dir, "motion_components.py")
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, motion_file)
            print(f"✅ Restaurado desde: {backup_file}")
            backup_found = True
            break
    
    if not backup_found:
        print("❌ No se encontró backup funcional")
        print("   Usa: python rollback_phase1_real.py")

print("\n" + "=" * 80)
print("PRÓXIMO PASO: python test_phase1_integration.py")
print("=" * 80)