#!/usr/bin/env python3
"""
🔧 FIX: Eliminar bloqueo en _apply_macro_rotation
⚡ Permite que rotación MS funcione incluso con IS activa
"""

import os
import shutil
from datetime import datetime

print("🔧 FIX DE BLOQUEO EN ROTACIÓN MACRO")
print("="*60)

# Archivo a modificar
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

if not os.path.exists(engine_file):
    print(f"❌ No se encuentra {engine_file}")
    exit(1)

# Backup
backup_file = f"{engine_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(engine_file, backup_file)
print(f"✅ Backup creado: {backup_file}")

# Leer archivo
with open(engine_file, 'r') as f:
    lines = f.readlines()

# Buscar y corregir el bloqueo
print("\n🔍 Buscando bloqueo en _apply_macro_rotation...")

fixed = False
for i in range(len(lines)):
    # Buscar la línea problemática
    if '_apply_macro_rotation' in lines[i]:
        # Buscar el continue que causa el bloqueo
        for j in range(i, min(i + 50, len(lines))):
            if 'individual_traj = motion.components.get("individual_trajectory")' in lines[j]:
                print(f"✅ Encontrado en línea {j+1}")
                
                # Buscar el continue asociado
                for k in range(j, min(j + 10, len(lines))):
                    if 'continue' in lines[k] and 'if individual_traj' in lines[k-1]:
                        print(f"❌ Bloqueo encontrado en línea {k+1}: {lines[k].strip()}")
                        
                        # Comentar las líneas del bloqueo
                        lines[k-1] = '                # ' + lines[k-1].lstrip()
                        lines[k] = '                # ' + lines[k].lstrip()
                        
                        # Agregar comentario explicativo
                        lines[k] = lines[k].rstrip() + '  # FIXED: Permitir rotación MS con IS\n'
                        
                        fixed = True
                        print("✅ Bloqueo eliminado (comentado)")
                        break
                if fixed:
                    break
        if fixed:
            break

if fixed:
    # Guardar cambios
    with open(engine_file, 'w') as f:
        f.writelines(lines)
    print("\n✅ Archivo actualizado exitosamente")
else:
    print("\n⚠️ No se encontró el patrón exacto del bloqueo")
    print("Puede que ya esté corregido o tenga un formato diferente")

# Verificar el cambio
print("\n🔍 Verificando cambio...")
with open(engine_file, 'r') as f:
    content = f.read()
    
if '# FIXED: Permitir rotación MS con IS' in content:
    print("✅ Cambio verificado correctamente")
else:
    print("⚠️ No se pudo verificar el cambio")

print("\n✅ Fix completado")
print(f"💡 Para revertir: cp {backup_file} {engine_file}")