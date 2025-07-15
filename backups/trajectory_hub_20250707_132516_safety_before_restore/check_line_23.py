#!/usr/bin/env python3
"""
🔍 VER QUÉ HAY EN LA LÍNEA 23
"""

import os

print("""
================================================================================
🔍 VERIFICANDO LÍNEA 23 Y CONTEXTO
================================================================================
""")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# Leer y mostrar contexto
with open(engine_file, 'r') as f:
    lines = f.readlines()

print("📋 Contexto alrededor de línea 23 (líneas 15-30):")
print("=" * 70)

for i in range(14, min(30, len(lines))):
    marker = ">>>" if i == 22 else "   "
    # Mostrar con repr para ver caracteres ocultos
    print(f"{marker} {i+1:3d}: {repr(lines[i])}")

# Analizar el problema
print("\n" + "=" * 70)
print("🔍 ANÁLISIS:")
print("=" * 70)

# Verificar si hay paréntesis sin cerrar
open_parens = 0
for i in range(18, 25):
    if i < len(lines):
        open_parens += lines[i].count('(')
        open_parens -= lines[i].count(')')
        print(f"Línea {i+1}: '(' = {lines[i].count('(')}, ')' = {lines[i].count(')')}, Balance = {open_parens}")

if open_parens > 0:
    print(f"\n❌ HAY {open_parens} PARÉNTESIS SIN CERRAR")
    print("   El import multilínea no está cerrado antes del siguiente import")

# Crear fix específico
print("\n" + "=" * 70)
print("🔧 CREANDO FIX ESPECÍFICO...")
print("=" * 70)

fix_code = '''#!/usr/bin/env python3
"""
✅ FIX FINAL - CERRAR PARÉNTESIS Y ORDENAR IMPORTS
"""

import os

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# Leer archivo
with open(engine_file, 'r') as f:
    lines = f.readlines()

# Buscar el import de motion_components
motion_import_start = None
for i, line in enumerate(lines):
    if 'from trajectory_hub.core.motion_components import (' in line:
        motion_import_start = i
        break

if motion_import_start is not None:
    print(f"✓ Import de motion_components encontrado en línea {motion_import_start + 1}")
    
    # Buscar dónde debe terminar (última línea con AdvancedOrientationModulation)
    import_end = None
    for i in range(motion_import_start + 1, min(motion_import_start + 10, len(lines))):
        if 'AdvancedOrientationModulation' in lines[i]:
            import_end = i
            break
    
    if import_end is not None:
        print(f"✓ Fin del import encontrado en línea {import_end + 1}")
        
        # Reconstruir el archivo
        new_lines = []
        
        # Copiar hasta el import
        new_lines.extend(lines[:motion_import_start])
        
        # Añadir el import completo y bien formateado
        new_lines.append('from trajectory_hub.core.motion_components import (\\n')
        
        # Copiar las líneas del import
        for i in range(motion_import_start + 1, import_end + 1):
            new_lines.append(lines[i])
        
        # Cerrar el paréntesis si no está cerrado
        if ')' not in lines[import_end]:
            new_lines.append(')\\n')
        
        # Añadir línea vacía
        new_lines.append('\\n')
        
        # Añadir import de ConcentrationComponent
        new_lines.append('from trajectory_hub.core.concentration_component import ConcentrationComponent\\n')
        
        # Saltar líneas problemáticas y continuar con el resto
        skip_until = import_end + 1
        while skip_until < len(lines) and ('ConcentrationComponent' in lines[skip_until] or lines[skip_until].strip() in ['', ',', ')']):
            skip_until += 1
        
        # Añadir el resto
        new_lines.extend(lines[skip_until:])
        
        # Guardar
        with open(engine_file, 'w') as f:
            f.writelines(new_lines)
        
        print("✅ Archivo arreglado correctamente")
        
        # Verificar sintaxis
        import ast
        try:
            with open(engine_file, 'r') as f:
                ast.parse(f.read())
            print("✅ SINTAXIS VERIFICADA - TODO CORRECTO")
        except SyntaxError as e:
            print(f"❌ Aún hay error: {e}")
    else:
        print("❌ No se encontró el final del import")
else:
    print("❌ No se encontró el import de motion_components")
'''

with open("fix_final_parens.py", 'w') as f:
    f.write(fix_code)
os.chmod("fix_final_parens.py", 0o755)

print("\n✅ Script de fix creado: fix_final_parens.py")
print("\nEjecuta: python fix_final_parens.py")