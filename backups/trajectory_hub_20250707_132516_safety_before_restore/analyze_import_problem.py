#!/usr/bin/env python3
"""
🔍 ANÁLISIS DETALLADO DEL PROBLEMA DE IMPORTS
"""

import os

print("""
================================================================================
🔍 ANÁLISIS DETALLADO DEL PROBLEMA
================================================================================
Vamos a examinar exactamente qué hay en el archivo
================================================================================
""")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

# 1. Leer y mostrar las líneas problemáticas
print("📋 CONTENIDO ACTUAL (líneas 10-35):")
print("=" * 70)

try:
    with open(engine_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i in range(9, min(35, len(lines))):
        # Marcar la línea problemática
        marker = ">>>" if i == 19 else "   "
        # Mostrar espacios y tabs claramente
        line_display = lines[i].replace('\t', '→   ').rstrip()
        print(f"{marker} {i+1:3d}: {repr(lines[i].rstrip())}")
        
except Exception as e:
    print(f"❌ Error leyendo archivo: {e}")
    exit(1)

# 2. Analizar el problema específico
print("\n" + "=" * 70)
print("🔍 ANÁLISIS DEL PROBLEMA:")
print("=" * 70)

# Buscar patrones
has_from_statement = False
indented_imports = []
import_start = None

for i, line in enumerate(lines):
    # Buscar declaraciones from
    if line.strip().startswith('from trajectory_hub.core.motion_components'):
        has_from_statement = True
        import_start = i
        print(f"✓ Encontrada declaración 'from' en línea {i+1}")
        
    # Buscar líneas con indentación que parecen ser parte de imports
    if line.startswith('    ') and ',' in line and 'Trajectory' in line:
        indented_imports.append(i)

if not has_from_statement:
    print("❌ NO HAY declaración 'from trajectory_hub.core.motion_components import ('")
    print("   Las líneas con imports están huérfanas")

if indented_imports:
    print(f"\n📍 Líneas con indentación que parecen imports: {[i+1 for i in indented_imports]}")

# 3. Diagnóstico
print("\n" + "=" * 70)
print("💡 DIAGNÓSTICO:")
print("=" * 70)

print("""
El problema es que:
1. Las líneas 20-23 tienen indentación (4 espacios)
2. NO hay una declaración 'from ... import (' antes
3. Por eso Python dice "unexpected indent"

Causa probable:
- Los scripts anteriores eliminaron la línea 'from ... import ('
- Pero dejaron las líneas siguientes con su indentación original
""")

# 4. Mostrar cómo DEBERÍA verse
print("\n" + "=" * 70)
print("✅ CÓMO DEBERÍA VERSE:")
print("=" * 70)

correct_import = """# Importar el sistema de componentes
from trajectory_hub.core.motion_components import (
    SourceMotion, TrajectoryMovementMode, TrajectoryDisplacementMode,
    OrientationModulation, IndividualTrajectory, TrajectoryTransform,
    MacroTrajectory, create_complex_movement, MotionState,
    AdvancedOrientationModulation
)
from trajectory_hub.core.concentration_component import ConcentrationComponent"""

print(correct_import)

# 5. Proponer solución
print("\n" + "=" * 70)
print("🛠️ SOLUCIÓN PROPUESTA:")
print("=" * 70)

print("""
Necesitamos:
1. Añadir 'from trajectory_hub.core.motion_components import (' antes de línea 20
2. Asegurar que el paréntesis se cierre correctamente
3. Poner el import de ConcentrationComponent en su propia línea

¿Deseas que cree un script para arreglar esto automáticamente?
O prefieres hacerlo manualmente con las instrucciones claras.
""")

# 6. Crear script de arreglo definitivo
fix_script = '''#!/usr/bin/env python3
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
    new_lines.append('from trajectory_hub.core.motion_components import (\\n')
    
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
    new_lines.append('from trajectory_hub.core.concentration_component import ConcentrationComponent\\n')
    
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
'''

with open("definitive_fix.py", 'w') as f:
    f.write(fix_script)
os.chmod("definitive_fix.py", 0o755)

print("\n✅ Script de arreglo creado: definitive_fix.py")