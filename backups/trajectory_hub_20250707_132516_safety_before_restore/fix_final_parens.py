#!/usr/bin/env python3
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
        new_lines.append('from trajectory_hub.core.motion_components import (\n')
        
        # Copiar las líneas del import
        for i in range(motion_import_start + 1, import_end + 1):
            new_lines.append(lines[i])
        
        # Cerrar el paréntesis si no está cerrado
        if ')' not in lines[import_end]:
            new_lines.append(')\n')
        
        # Añadir línea vacía
        new_lines.append('\n')
        
        # Añadir import de ConcentrationComponent
        new_lines.append('from trajectory_hub.core.concentration_component import ConcentrationComponent\n')
        
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
