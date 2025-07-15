# === fix_line_1000_syntax.py ===
# 🔧 Fix del error de sintaxis en línea 1000
# ⚡ Error encontrado: if component is not None.enabled:

import os
import shutil
from datetime import datetime

print("🎯 Arreglando error de sintaxis en línea 1000\n")

# Archivo a modificar
filepath = './trajectory_hub/core/motion_components.py'

# Backup
backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
shutil.copy2(filepath, backup_path)
print(f"✅ Backup creado: {backup_path}")

# Leer archivo
with open(filepath, 'r') as f:
    lines = f.readlines()

# Buscar y corregir la línea problemática
fixed = False
for i, line in enumerate(lines):
    if i == 999:  # Línea 1000 (índice 999)
        print(f"\n❌ Línea {i+1} actual:")
        print(f"   {line.rstrip()}")
        
        # Corregir la sintaxis
        if "if component is not None.enabled:" in line:
            indent = len(line) - len(line.lstrip())
            lines[i] = " " * indent + "if component is not None and getattr(component, 'enabled', False):\n"
            print(f"\n✅ Línea {i+1} corregida:")
            print(f"   {lines[i].rstrip()}")
            fixed = True
        else:
            print(f"\n⚠️ La línea no coincide exactamente. Contenido actual:")
            print(f"   '{line.strip()}'")
            
            # Intentar corregir de todos modos si contiene el patrón
            if "component is not None.enabled" in line:
                indent = len(line) - len(line.lstrip())
                lines[i] = " " * indent + "if component is not None and getattr(component, 'enabled', False):\n"
                print(f"\n✅ Línea corregida de todos modos:")
                print(f"   {lines[i].rstrip()}")
                fixed = True

# Escribir cambios
if fixed:
    with open(filepath, 'w') as f:
        f.writelines(lines)
    print("\n✅ Archivo corregido exitosamente")
    
    # Verificar alrededor de la línea corregida
    print("\n📋 Contexto de la corrección (líneas 995-1005):")
    for i in range(max(0, 995), min(len(lines), 1005)):
        marker = ">>>" if i == 999 else "   "
        print(f"{marker} {i+1}: {lines[i].rstrip()}")
else:
    print("\n❌ No se pudo corregir la línea")

print("\n🔄 Ejecuta ahora: python test_rotation_ms_final.py")