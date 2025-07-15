#!/usr/bin/env python3
"""
🔍 VERIFICAR FIRMAS DE UPDATE()
"""

import inspect
import os
import sys

current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

print("""
================================================================================
🔍 VERIFICANDO FIRMAS DE UPDATE()
================================================================================
""")

# Suprimir warnings
os.environ['DISABLE_OSC'] = '1'

try:
    # 1. Verificar EnhancedTrajectoryEngine.update()
    print("1️⃣ EnhancedTrajectoryEngine.update():")
    print("-" * 50)
    
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    
    # Obtener firma
    sig = inspect.signature(EnhancedTrajectoryEngine.update)
    print(f"   Firma: {sig}")
    
    # Ver el código fuente (primeras líneas)
    try:
        source = inspect.getsource(EnhancedTrajectoryEngine.update)
        lines = source.split('\n')[:5]
        print("   Código:")
        for line in lines:
            print(f"      {line}")
    except:
        print("   No se pudo obtener el código fuente")
    
    # 2. Verificar SourceMotion.update()
    print("\n2️⃣ SourceMotion.update():")
    print("-" * 50)
    
    from trajectory_hub.core.motion_components import SourceMotion
    
    sig = inspect.signature(SourceMotion.update)
    print(f"   Firma: {sig}")
    
    try:
        source = inspect.getsource(SourceMotion.update)
        lines = source.split('\n')[:5]
        print("   Código:")
        for line in lines:
            print(f"      {line}")
    except:
        print("   No se pudo obtener el código fuente")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# 3. Buscar en el archivo directamente
print("\n3️⃣ BÚSQUEDA DIRECTA EN enhanced_trajectory_engine.py:")
print("-" * 50)

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
if os.path.exists(engine_file):
    with open(engine_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar def update(
    for i, line in enumerate(lines):
        if 'def update(' in line and not line.strip().startswith('#'):
            print(f"   Línea {i+1}: {line.strip()}")
            # Mostrar las siguientes 3 líneas
            for j in range(1, 4):
                if i+j < len(lines):
                    print(f"   Línea {i+j+1}: {lines[i+j].rstrip()}")
            break

print("\n" + "="*70)
print("📋 DIAGNÓSTICO:")
print("="*70)

print("""
Si engine.update() no acepta parámetros pero debería:
1. Necesitamos modificar EnhancedTrajectoryEngine.update()
2. O crear un wrapper que maneje el dt

Si engine.update() ya maneja dt internamente:
1. Los tests deben llamar engine.update() sin parámetros
""")

# 4. Crear script de arreglo
fix_script = '''#!/usr/bin/env python3
"""
🔧 ARREGLAR FIRMA DE ENGINE.UPDATE()
"""

import os
import re

print("🔧 ARREGLANDO engine.update()...")

engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"

with open(engine_file, 'r') as f:
    content = f.read()

# Buscar def update(self):
if 'def update(self):' in content:
    print("✅ Encontrado update(self), cambiando a update(self, dt=None)")
    content = content.replace('def update(self):', 'def update(self, dt=None):')
    
    # Añadir manejo de dt si no existe
    lines = content.split('\\n')
    for i, line in enumerate(lines):
        if 'def update(self, dt=None):' in line:
            # Ver si las siguientes líneas manejan dt
            if i+1 < len(lines) and 'if dt is None:' not in lines[i+1]:
                # Insertar manejo de dt
                indent = '        '
                lines.insert(i+1, f'{indent}if dt is None:')
                lines.insert(i+2, f'{indent}    dt = 1.0 / self.fps')
                break
    
    content = '\\n'.join(lines)
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("✅ engine.update() ahora acepta dt")
else:
    print("❓ No se encontró def update(self):")
    print("   Verificando manualmente...")
'''

with open("fix_engine_update_signature.py", 'w') as f:
    f.write(fix_script)
os.chmod("fix_engine_update_signature.py", 0o755)

print("\n✅ Script de arreglo creado: fix_engine_update_signature.py")