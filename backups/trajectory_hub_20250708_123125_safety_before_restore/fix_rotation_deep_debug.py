# === fix_rotation_deep_debug.py ===
# 🔧 Fix: Debug profundo - encontrar TODAS las comparaciones problemáticas
# ⚡ 5 minutos finales

import os
import re
import traceback

print("🔍 DEBUG PROFUNDO - ENCONTRAR EL ERROR REAL")
print("="*50)

# Paso 1: Crear un test que capture el error exacto
test_code = '''
import numpy as np
import sys
import traceback
sys.path.append('.')

from trajectory_hub import EnhancedTrajectoryEngine

# Crear engine y macro
engine = EnhancedTrajectoryEngine(n_sources=4, update_rate=60)
sids = []
for i in range(4):
    sid = engine.create_source(f"test_{i}")
    sids.append(sid)

# Crear macro
engine.create_macro("test_macro", sids)

# Aplicar rotación
engine.set_macro_rotation("test_macro", speed_x=0.0, speed_y=1.0, speed_z=0.0)

# Intentar update y capturar el error exacto
try:
    engine.update()
except Exception as e:
    print(f"\\n❌ ERROR CAPTURADO: {e}")
    print(f"\\nTRACEBACK COMPLETO:")
    traceback.print_exc()
    
    # Información adicional
    print(f"\\n📍 INFORMACIÓN DEL ERROR:")
    print(f"   Tipo: {type(e).__name__}")
    print(f"   Archivo: {traceback.extract_tb(e.__traceback__)[-1].filename}")
    print(f"   Línea: {traceback.extract_tb(e.__traceback__)[-1].lineno}")
    print(f"   Función: {traceback.extract_tb(e.__traceback__)[-1].name}")
'''

with open("debug_error_location.py", "w") as f:
    f.write(test_code)

print("\n🧪 Ejecutando debug para localizar el error exacto...")
os.system("python debug_error_location.py > error_output.txt 2>&1")

# Leer el output
with open("error_output.txt", "r") as f:
    error_output = f.read()
    print(error_output)

# Paso 2: Buscar el patrón del error en motion_components.py
print("\n🔍 Buscando comparaciones problemáticas en motion_components.py...")

with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Buscar patrones problemáticos
problematic_patterns = [
    r'if\s+self\.',  # if self.algo (puede ser array)
    r'if\s+not\s+self\.',  # if not self.algo
    r'if\s+.*enabled',  # cualquier check de enabled
    r'if\s+.*speed',  # cualquier check de speed
]

fixes_needed = []
for i, line in enumerate(lines):
    for pattern in problematic_patterns:
        if re.search(pattern, line) and 'isinstance' not in line:
            # Verificar si es en MacroRotation o update_with_deltas
            # Buscar la clase actual
            current_class = None
            for j in range(i, -1, -1):
                if 'class ' in lines[j]:
                    current_class = lines[j].strip()
                    break
            
            if current_class and ('MacroRotation' in current_class or 'SourceMotion' in current_class):
                print(f"   Línea {i+1} en {current_class}: {line.strip()}")
                fixes_needed.append((i, line, current_class))

# Paso 3: Aplicar fixes específicos
print(f"\n🔧 Aplicando {len(fixes_needed)} correcciones...")

for line_num, line, class_name in fixes_needed:
    original = lines[line_num]
    
    # Fix para enabled
    if 'if not self.enabled:' in line and 'MacroRotation' in class_name:
        lines[line_num] = line.replace(
            'if not self.enabled:',
            'if not getattr(self, "enabled", False):'
        )
        print(f"✅ Corregido línea {line_num+1}: check de enabled")
    
    # Fix para update_with_deltas
    elif 'if component' in line and 'SourceMotion' in class_name:
        # Este es probablemente el problema real
        lines[line_num] = line.replace(
            'if component',
            'if component is not None'
        )
        print(f"✅ Corregido línea {line_num+1}: check de component")

# Guardar cambios
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("\n✅ motion_components.py actualizado")

# Limpiar archivos temporales
os.remove("debug_error_location.py")
os.remove("error_output.txt")

# Paso 4: Test final
print("\n" + "="*50)
print("🎯 ÚLTIMO INTENTO...")
print("="*50)
os.system("python test_rotation_ms_final.py")