#!/usr/bin/env python3
"""
🔧 FIX DIRECTO DE SOURCEMOTION
"""

import os
import re

print("""
================================================================================
🔧 FIX DIRECTO DE SOURCEMOTION
================================================================================
Vamos a encontrar y arreglar SourceMotion directamente
================================================================================
""")

motion_file = "trajectory_hub/core/motion_components.py"

# 1. Primero, veamos qué hay en SourceMotion
print("🔍 Buscando clase SourceMotion...")

with open(motion_file, 'r') as f:
    lines = f.readlines()

# Buscar la clase SourceMotion
source_motion_start = None
init_start = None
init_end = None

for i, line in enumerate(lines):
    if 'class SourceMotion' in line and not line.strip().startswith('#'):
        source_motion_start = i
        print(f"✅ Encontrada clase SourceMotion en línea {i+1}")
        
        # Buscar su __init__
        for j in range(i, min(i + 50, len(lines))):
            if 'def __init__(self' in lines[j]:
                init_start = j
                print(f"✅ Encontrado __init__ en línea {j+1}")
                
                # Buscar el final del __init__ (siguiente def o class)
                for k in range(j + 1, min(j + 100, len(lines))):
                    # Si encontramos otro método o clase al mismo nivel de indentación
                    if (lines[k].strip() and 
                        not lines[k].startswith('        ') and  # No es parte del método
                        (lines[k].strip().startswith('def ') or 
                         lines[k].strip().startswith('class ') or
                         lines[k].strip().startswith('@'))):
                        init_end = k
                        break
                
                if init_end is None:
                    # Buscar por cambio de indentación
                    for k in range(j + 1, min(j + 100, len(lines))):
                        if lines[k].strip() and not lines[k].startswith('    '):
                            init_end = k
                            break
                
                break
        break

if init_start is not None and init_end is not None:
    print(f"\n📋 Método __init__ encontrado (líneas {init_start+1} a {init_end})")
    
    # Verificar si ya tiene motion_components
    init_content = ''.join(lines[init_start:init_end])
    
    if 'motion_components' not in init_content:
        print("❌ No tiene motion_components, añadiendo...")
        
        # Buscar la última línea de código en __init__ (antes de comentarios finales)
        insert_line = init_end - 1
        for i in range(init_end - 1, init_start, -1):
            line = lines[i].strip()
            if line and not line.startswith('#') and 'self.' in lines[i]:
                insert_line = i + 1
                break
        
        # Detectar indentación
        indent = '        '  # Default 8 espacios
        for i in range(init_start + 1, init_end):
            if lines[i].strip() and 'self.' in lines[i]:
                match = re.match(r'^(\s+)self\.', lines[i])
                if match:
                    indent = match.group(1)
                    break
        
        # Insertar código de deltas
        delta_code = [
            f'\n{indent}# Sistema de componentes para arquitectura de deltas\n',
            f'{indent}self.motion_components = {{}}  # Dict[str, MotionComponent]\n',
            f'{indent}self.component_weights = {{}}  # Pesos para cada componente\n',
            f'{indent}self.use_delta_system = False  # Flag para migración gradual\n'
        ]
        
        # Insertar
        for code in reversed(delta_code):
            lines.insert(insert_line, code)
        
        print("✅ Atributos del sistema de deltas añadidos")
    else:
        print("✅ Ya tiene motion_components")
    
    # 2. Ahora verificar el método update()
    print("\n🔍 Buscando método update()...")
    
    update_start = None
    update_end = None
    
    for i in range(source_motion_start, len(lines)):
        if 'def update(self' in lines[i] and not lines[i].strip().startswith('#'):
            update_start = i
            print(f"✅ Encontrado update() en línea {i+1}")
            
            # Verificar firma
            if 'def update(self):' in lines[i]:
                print("❌ update() no acepta dt, corrigiendo...")
                lines[i] = lines[i].replace('def update(self):', 'def update(self, dt: float = None):')
                
                # Añadir manejo de dt
                indent = '        '
                lines.insert(i + 1, f'{indent}if dt is None:\n')
                lines.insert(i + 2, f'{indent}    dt = 1.0 / 60.0  # Default 60 FPS\n')
                print("✅ Firma de update() corregida")
            
            break
    
    # 3. Guardar cambios
    print("\n💾 Guardando cambios...")
    with open(motion_file, 'w') as f:
        f.writelines(lines)
    print("✅ Archivo actualizado")
    
else:
    print("❌ No se pudo encontrar SourceMotion.__init__")

# 4. Verificación final
print("\n🧪 VERIFICACIÓN FINAL...")
print("-" * 50)

test_code = '''
import os
import sys

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

# Limpiar imports anteriores
if 'trajectory_hub.core.motion_components' in sys.modules:
    del sys.modules['trajectory_hub.core.motion_components']

try:
    from trajectory_hub.core.motion_components import SourceMotion
    
    # Verificar que podemos crear una instancia con source_id
    motion = SourceMotion(source_id=0)
    
    # Verificar atributos
    attrs = ['motion_components', 'component_weights', 'use_delta_system']
    
    for attr in attrs:
        if hasattr(motion, attr):
            print(f"✅ {attr}: {getattr(motion, attr)}")
        else:
            print(f"❌ Falta {attr}")
    
    # Verificar update con dt
    try:
        motion.update(0.016)
        print("✅ update(dt) funciona")
    except TypeError as e:
        print(f"❌ update(dt) error: {e}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
'''

exec(test_code)

print("""

================================================================================
📋 ESTADO ACTUAL
================================================================================

Si todos los checks son ✅, ejecuta:
python test_concentration_delta.py

Si aún hay errores, podemos:
1. Editar manualmente el archivo
2. Revisar la estructura de SourceMotion

================================================================================
""")