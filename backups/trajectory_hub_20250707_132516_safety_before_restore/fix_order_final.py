#!/usr/bin/env python3
"""
✅ FIX DEFINITIVO - REORDENAR LÍNEAS CORRECTAMENTE
"""

import os
import ast

print("""
================================================================================
✅ FIX DEFINITIVO - REORDENANDO LÍNEAS
================================================================================
El problema es que las líneas están desordenadas.
Vamos a ponerlas en el orden correcto.
================================================================================
""")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# Backup
backup_name = f"{engine_file}.backup_order_fix"
with open(engine_file, 'r') as f:
    original_content = f.read()
with open(backup_name, 'w') as f:
    f.write(original_content)
print(f"✅ Backup creado: {backup_name}")

# Leer líneas
with open(engine_file, 'r') as f:
    lines = f.readlines()

print("\n📋 Estado actual de las líneas problemáticas:")
for i in range(18, min(30, len(lines))):
    print(f"  {i+1:3d}: {lines[i].rstrip()}")

# Reconstruir el archivo correctamente
new_lines = []
i = 0

while i < len(lines):
    # Si encontramos el comentario de imports
    if '# Importar el sistema de componentes' in lines[i]:
        new_lines.append(lines[i])  # Añadir comentario
        i += 1
        
        # Añadir import de motion_components COMPLETO y CORRECTO
        new_lines.append('from trajectory_hub.core.motion_components import (\n')
        new_lines.append('    SourceMotion, TrajectoryMovementMode, TrajectoryDisplacementMode,\n')
        new_lines.append('    OrientationModulation, IndividualTrajectory, TrajectoryTransform,\n')
        new_lines.append('    MacroTrajectory, create_complex_movement, MotionState,\n')
        new_lines.append('    AdvancedOrientationModulation\n')
        new_lines.append(')\n')
        new_lines.append('from trajectory_hub.core.concentration_component import ConcentrationComponent\n')
        
        # Saltar todas las líneas problemáticas hasta encontrar el siguiente import válido
        while i < len(lines):
            line = lines[i]
            # Si encontramos un import que NO sea de motion_components o concentration_component
            if (line.strip().startswith('from ') and 
                'motion_components' not in line and 
                'concentration_component' not in line and
                'ConcentrationComponent' not in line):
                break
            # Si encontramos algo que no sea parte de los imports problemáticos
            elif (line.strip() and 
                  not line.strip().startswith(('SourceMotion', 'OrientationModulation', 
                                               'MacroTrajectory', 'AdvancedOrientationModulation',
                                               'ConcentrationComponent', ',', ')'))):
                break
            i += 1
        continue
    
    # Para cualquier otra línea, simplemente copiar
    new_lines.append(lines[i])
    i += 1

# Guardar archivo corregido
print("\n💾 Guardando archivo corregido...")
with open(engine_file, 'w') as f:
    f.writelines(new_lines)

# Verificar sintaxis
print("\n🧪 Verificando sintaxis...")
try:
    with open(engine_file, 'r') as f:
        content = f.read()
    ast.parse(content)
    print("✅ ¡SINTAXIS CORRECTA!")
    
    # Mostrar cómo quedó
    print("\n📋 Líneas corregidas:")
    with open(engine_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar y mostrar la sección de imports
    for i, line in enumerate(lines):
        if '# Importar el sistema de componentes' in line:
            for j in range(i, min(i+10, len(lines))):
                print(f"  {j+1:3d}: {lines[j].rstrip()}")
            break
    
    print("""
================================================================================
✅ ARCHIVO ARREGLADO CORRECTAMENTE
================================================================================

Los imports ahora están en el orden correcto:
1. Import de motion_components (multilínea)
2. Import de concentration_component (una línea)

PRÓXIMO PASO:
python continue_implementation.py
================================================================================
""")
    
except SyntaxError as e:
    print(f"❌ Error de sintaxis en línea {e.lineno}: {e.msg}")
    print("\nMostrando contexto del error:")
    lines = content.split('\n')
    if e.lineno:
        start = max(0, e.lineno - 5)
        end = min(len(lines), e.lineno + 5)
        for i in range(start, end):
            marker = ">>>" if i == e.lineno - 1 else "   "
            print(f"{marker} {i+1:3d}: {lines[i]}")