#!/usr/bin/env python3
"""
🧹 LIMPIEZA TOTAL DE IMPORTS
"""

import os
import ast

print("""
================================================================================
🧹 LIMPIEZA TOTAL DE IMPORTS
================================================================================
Vamos a reconstruir la sección de imports desde cero
================================================================================
""")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# Leer el archivo
with open(engine_file, 'r') as f:
    lines = f.readlines()

# Identificar qué clases necesitamos importar de motion_components
motion_components_classes = [
    'SourceMotion', 'TrajectoryMovementMode', 'TrajectoryDisplacementMode',
    'OrientationModulation', 'IndividualTrajectory', 'TrajectoryTransform',
    'MacroTrajectory', 'create_complex_movement', 'MotionState',
    'AdvancedOrientationModulation'
]

# Reconstruir el archivo
new_lines = []
i = 0
imports_fixed = False

while i < len(lines):
    line = lines[i]
    
    # Si encontramos el comentario de imports y no lo hemos arreglado aún
    if '# Importar el sistema de componentes' in line and not imports_fixed:
        # Añadir el comentario
        new_lines.append(line)
        
        # Añadir el import correcto de motion_components
        new_lines.append('from trajectory_hub.core.motion_components import (\n')
        for j, class_name in enumerate(motion_components_classes):
            if j < len(motion_components_classes) - 1:
                new_lines.append(f'    {class_name},\n')
            else:
                new_lines.append(f'    {class_name}\n')
        new_lines.append(')\n')
        
        # Añadir import de ConcentrationComponent
        new_lines.append('from trajectory_hub.core.concentration_component import ConcentrationComponent\n')
        
        # Marcar que ya arreglamos los imports
        imports_fixed = True
        
        # Saltar todas las líneas hasta encontrar un import que NO sea de estos módulos
        i += 1
        while i < len(lines):
            current_line = lines[i].strip()
            
            # Si es una línea vacía, la mantenemos
            if not current_line:
                new_lines.append('\n')
                i += 1
                continue
            
            # Si es un comentario, lo mantenemos y continuamos
            if current_line.startswith('#') and 'Importar el sistema' not in current_line:
                new_lines.append(lines[i])
                i += 1
                continue
            
            # Si es un import diferente (no motion_components ni concentration_component)
            if (current_line.startswith('from ') and 
                'motion_components' not in current_line and
                'concentration_component' not in current_line):
                # Hemos llegado al siguiente import, continuamos normalmente
                break
            
            # Si es parte de los imports problemáticos, lo saltamos
            skip_patterns = [
                'SourceMotion', 'TrajectoryMovementMode', 'OrientationModulation',
                'ConcentrationComponent', 'AdvancedOrientationModulation',
                'from trajectory_hub.core.motion_components',
                'from trajectory_hub.core.concentration_component',
                ',', ')'
            ]
            
            if any(pattern in current_line for pattern in skip_patterns):
                i += 1
                continue
            
            # Si llegamos aquí y no es un import conocido, salimos del bucle
            if not current_line.startswith(('    ', 'from ')):
                break
                
            i += 1
        continue
    
    # Para cualquier otra línea, copiar normalmente
    new_lines.append(line)
    i += 1

# Guardar
print("💾 Guardando archivo limpio...")
with open(engine_file, 'w') as f:
    f.writelines(new_lines)

# Verificar sintaxis
print("\n🧪 Verificando sintaxis...")
try:
    with open(engine_file, 'r') as f:
        content = f.read()
    ast.parse(content)
    print("✅ ¡SINTAXIS CORRECTA!")
    
    # Mostrar la sección arreglada
    print("\n📋 Sección de imports arreglada:")
    print("-" * 70)
    with open(engine_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar y mostrar
    for i, line in enumerate(lines):
        if '# Importar el sistema de componentes' in line:
            for j in range(i, min(i + 15, len(lines))):
                if lines[j].strip() and not lines[j].strip().startswith(('from trajectory_hub.core.motion',
                                                                         'from trajectory_hub.core.concentration',
                                                                         'SourceMotion', 'Trajectory', 
                                                                         'Orientation', 'Macro', 'Advanced',
                                                                         ')', ',')):
                    break
                print(f"{j+1:3d}: {lines[j]}", end='')
            break
    
    print("-" * 70)
    print("""
✅ IMPORTS ARREGLADOS CORRECTAMENTE

PRÓXIMO PASO:
python continue_implementation.py
""")
    
except SyntaxError as e:
    print(f"❌ Todavía hay error de sintaxis en línea {e.lineno}: {e.msg}")
    print("\nRevisa manualmente el archivo o ejecuta:")
    print("python show_current_state.py")
    
# Crear script para mostrar estado actual
show_state = '''#!/usr/bin/env python3
"""Mostrar estado actual del archivo"""
import os

with open("trajectory_hub/core/enhanced_trajectory_engine.py", 'r') as f:
    lines = f.readlines()

print("PRIMERAS 50 LÍNEAS:")
print("=" * 70)
for i in range(min(50, len(lines))):
    print(f"{i+1:3d}: {lines[i]}", end='')
'''

with open("show_current_state.py", 'w') as f:
    f.write(show_state)
os.chmod("show_current_state.py", 0o755)