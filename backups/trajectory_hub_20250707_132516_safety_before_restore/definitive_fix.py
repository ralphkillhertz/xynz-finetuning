#!/usr/bin/env python3
"""
✅ ARREGLO DEFINITIVO Y SIMPLE
"""

import os

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# Leer archivo
with open(engine_file, 'r') as f:
    lines = f.readlines()

# Buscar la línea con "# Importar el sistema de componentes"
import_comment_line = None
for i, line in enumerate(lines):
    if '# Importar el sistema de componentes' in line:
        import_comment_line = i
        break

if import_comment_line is not None:
    # Reemplazar desde ahí hasta encontrar una línea que no empiece con espacios
    # y no sea parte del import
    
    new_lines = lines[:import_comment_line+1]
    
    # Añadir el import correcto
    new_lines.append('from trajectory_hub.core.motion_components import (\n')
    
    # Buscar las líneas del import (con indentación)
    i = import_comment_line + 1
    while i < len(lines):
        line = lines[i]
        # Si es una línea con indentación y contiene nombres de clases
        if line.startswith('    ') and ('Motion' in line or 'Trajectory' in line or ')' in line):
            new_lines.append(line)
            if ')' in line:
                i += 1
                break
        elif line.strip() == '':
            pass  # Saltar líneas vacías
        else:
            break
        i += 1
    
    # Añadir import de ConcentrationComponent
    new_lines.append('from trajectory_hub.core.concentration_component import ConcentrationComponent\n')
    
    # Añadir el resto del archivo
    # Buscar dónde continuar (saltar imports mal formateados)
    while i < len(lines) and ('ConcentrationComponent' in lines[i] or lines[i].strip() == ''):
        i += 1
    
    new_lines.extend(lines[i:])
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Archivo arreglado")
else:
    print("❌ No se encontró el comentario de imports")
