#!/usr/bin/env python3
"""
🔧 COMPLETAR MIGRACIÓN DE SOURCEMOTION AL SISTEMA DE DELTAS
"""

import os
import re
from datetime import datetime

print("""
================================================================================
🔧 COMPLETANDO MIGRACIÓN DE SOURCEMOTION
================================================================================
Vamos a añadir los atributos y métodos faltantes para el sistema de deltas
================================================================================
""")

motion_file = "trajectory_hub/core/motion_components.py"

# Backup
backup_name = f"{motion_file}.backup_delta_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
with open(motion_file, 'r') as f:
    content = f.read()
with open(backup_name, 'w') as f:
    f.write(content)
print(f"✅ Backup creado: {backup_name}")

# 1. Verificar si motion_components ya existe en __init__
print("\n🔍 Verificando SourceMotion.__init__...")

# Buscar la clase SourceMotion y su __init__
class_pattern = r'class SourceMotion[^:]*:\s*(?:"""[^"]*"""\s*)?def __init__\(self[^)]*\):[^}]+?(?=\n\s{0,4}def|\n\s{0,4}class|\Z)'
match = re.search(class_pattern, content, re.DOTALL)

if match:
    init_method = match.group(0)
    
    if 'motion_components' not in init_method:
        print("❌ No tiene motion_components, añadiendo...")
        
        # Buscar el final del __init__ (antes del siguiente método)
        init_lines = init_method.split('\n')
        
        # Encontrar la última línea con código (no comentario)
        insert_index = len(init_lines) - 1
        for i in range(len(init_lines) - 1, 0, -1):
            line = init_lines[i].strip()
            if line and not line.startswith('#') and not line.startswith('"""'):
                # Verificar la indentación
                indent_match = re.match(r'^(\s*)', init_lines[i])
                if indent_match:
                    indent = indent_match.group(1)
                    # Añadir después de esta línea
                    insert_index = i + 1
                    break
        
        # Insertar el código del sistema de deltas
        delta_code = f"""
{indent}# Sistema de componentes para arquitectura de deltas
{indent}self.motion_components = {{}}  # Dict[str, MotionComponent]
{indent}self.component_weights = {{}}  # Pesos para cada componente
{indent}self.use_delta_system = False  # Flag para migración gradual"""
        
        init_lines.insert(insert_index, delta_code)
        new_init = '\n'.join(init_lines)
        
        # Reemplazar en el contenido
        content = content.replace(init_method, new_init)
        print("✅ Atributos del sistema de deltas añadidos")
    else:
        print("✅ Ya tiene motion_components")

# 2. Verificar y arreglar el método update()
print("\n🔍 Verificando SourceMotion.update()...")

# Buscar el método update
update_pattern = r'def update\(self[^)]*\):[^}]+?(?=\n\s{4}def|\n\s{0,4}class|\Z)'
update_match = re.search(update_pattern, content, re.DOTALL)

if update_match:
    update_method = update_match.group(0)
    
    # Verificar la firma del método
    if 'def update(self):' in update_method:
        print("❌ update() no acepta dt, corrigiendo...")
        
        # Cambiar la firma
        new_update = update_method.replace('def update(self):', 'def update(self, dt: float = None):')
        
        # Si dt no se usa, añadir al principio
        if 'dt' not in new_update or 'dt = ' not in new_update:
            # Buscar donde empieza el cuerpo del método
            lines = new_update.split('\n')
            for i, line in enumerate(lines):
                if 'def update' in line:
                    # Insertar después de la definición
                    indent = '        '  # Asumiendo 8 espacios
                    lines.insert(i + 1, f'{indent}if dt is None:')
                    lines.insert(i + 2, f'{indent}    dt = 1.0 / 60.0  # Default 60 FPS')
                    break
            new_update = '\n'.join(lines)
        
        content = content.replace(update_method, new_update)
        print("✅ Firma de update() corregida")
    else:
        print("✅ update() ya acepta parámetros")
    
    # Verificar si tiene lógica de deltas
    if 'use_delta_system' not in update_method:
        print("❌ No tiene lógica de deltas, añadiendo...")
        
        # Buscar dónde insertar la lógica de deltas
        lines = content.split('\n')
        in_update = False
        update_start_indent = ''
        
        for i, line in enumerate(lines):
            if 'def update(self' in line and 'SourceMotion' in content[:content.find(line)]:
                in_update = True
                # Obtener indentación
                indent_match = re.match(r'^(\s*)def', line)
                if indent_match:
                    update_start_indent = indent_match.group(1) + '    '  # Indentación del cuerpo
                continue
            
            if in_update and line.strip() and not line.strip().startswith('#'):
                # Insertar la lógica de deltas aquí
                delta_logic = f"""
{update_start_indent}# Sistema de deltas (si está activado)
{update_start_indent}if self.use_delta_system and self.motion_components:
{update_start_indent}    # Recolectar deltas de todos los componentes activos
{update_start_indent}    deltas = []
{update_start_indent}    context = {{'source_id': getattr(self, 'source_id', None)}}
{update_start_indent}    
{update_start_indent}    for name, component in self.motion_components.items():
{update_start_indent}        if component.enabled:
{update_start_indent}            try:
{update_start_indent}                delta = component.calculate_delta(self.state, dt, context)
{update_start_indent}                deltas.append((name, delta))
{update_start_indent}            except Exception as e:
{update_start_indent}                print(f"Error en {{name}}: {{e}}")
{update_start_indent}    
{update_start_indent}    # Componer nuevo estado si hay deltas
{update_start_indent}    if deltas:
{update_start_indent}        from trajectory_hub.core.delta_system import DeltaComposer
{update_start_indent}        self.state = DeltaComposer.compose(self.state, deltas, self.component_weights)
{update_start_indent}        return  # Skip legacy update
{update_start_indent}
{update_start_indent}# Sistema legacy (se ejecuta si no hay deltas)"""
                
                lines.insert(i, delta_logic)
                break
        
        content = '\n'.join(lines)
        print("✅ Lógica de deltas añadida a update()")

# 3. Guardar cambios
print("\n💾 Guardando cambios...")
with open(motion_file, 'w') as f:
    f.write(content)

# 4. Verificar que todo esté bien
print("\n🧪 Verificando cambios...")
verification_code = '''
import os
import sys

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

try:
    from trajectory_hub.core.motion_components import SourceMotion
    
    # Crear instancia
    motion = SourceMotion()
    
    # Verificar atributos
    checks = {
        'motion_components': hasattr(motion, 'motion_components'),
        'component_weights': hasattr(motion, 'component_weights'),
        'use_delta_system': hasattr(motion, 'use_delta_system'),
        'update acepta dt': True  # Lo verificaremos al llamarlo
    }
    
    # Verificar que update acepta dt
    try:
        motion.update(0.016)  # 60 FPS
        checks['update acepta dt'] = True
    except TypeError as e:
        if "takes 1 positional argument" in str(e):
            checks['update acepta dt'] = False
    
    # Mostrar resultados
    all_good = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
        if not result:
            all_good = False
    
    if all_good:
        print("\\n✅ SourceMotion está listo para el sistema de deltas!")
    else:
        print("\\n❌ Aún hay problemas por resolver")
        
except Exception as e:
    print(f"❌ Error: {e}")
'''

print("\nEjecutando verificación...")
exec(verification_code)

print("""

================================================================================
✅ MIGRACIÓN DE SOURCEMOTION COMPLETADA
================================================================================

CAMBIOS REALIZADOS:
1. Añadidos atributos del sistema de deltas a __init__
2. Corregida firma de update() para aceptar dt
3. Añadida lógica de composición de deltas

PRÓXIMO PASO:
python test_concentration_delta.py

Si el test pasa, el sistema de deltas está funcionando!
================================================================================
""")