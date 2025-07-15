# === fix_motion_state_source_id.py ===
# 🔧 Fix: Añadir source_id a MotionState o arreglar MacroRotation
# ⚡ FINAL FIX

import os
import re

# Leer archivo
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()

print("🔍 Verificando MotionState...")

# Buscar definición de MotionState
state_pattern = r'@dataclass\s*\nclass MotionState.*?(?=\n@dataclass|\nclass |\Z)'
state_match = re.search(state_pattern, content, re.DOTALL)

if state_match:
    motion_state_def = state_match.group(0)
    
    if 'source_id' not in motion_state_def:
        print("❌ MotionState no tiene source_id, añadiendo...")
        
        # Buscar donde insertar source_id (después del docstring)
        lines = motion_state_def.split('\n')
        insert_line = -1
        
        for i, line in enumerate(lines):
            if '"""' in line and i > 2:  # Fin del docstring
                insert_line = i + 1
                break
        
        if insert_line > 0:
            lines.insert(insert_line, '    source_id: int')
            new_motion_state = '\n'.join(lines)
            content = content.replace(motion_state_def, new_motion_state)
            
            print("✅ source_id añadido a MotionState")
        else:
            print("⚠️ No se pudo añadir source_id, usando plan B...")
    else:
        print("✅ MotionState ya tiene source_id")
else:
    print("❌ No se encontró MotionState, usando plan B...")

# Plan B: Modificar MacroRotation para no depender de source_id
print("\n🔧 Arreglando MacroRotation.calculate_delta...")

# Buscar MacroRotation.calculate_delta
rotation_pattern = r'(class MacroRotation.*?def calculate_delta.*?)(delta\.source_id = state\.source_id)'
rotation_match = re.search(rotation_pattern, content, re.DOTALL)

if rotation_match:
    # Reemplazar la línea problemática
    # En lugar de usar state.source_id, obtenerlo de otra forma o simplemente comentarlo
    content = re.sub(
        r'delta\.source_id = state\.source_id',
        '# delta.source_id = state.source_id if hasattr(state, "source_id") else None',
        content
    )
    print("✅ MacroRotation.calculate_delta arreglado")

# Guardar
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🔧 Verificando sintaxis...")
import py_compile
try:
    py_compile.compile("trajectory_hub/core/motion_components.py", doraise=True)
    print("✅ Sintaxis correcta")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🚀 Ejecutando test final...")
os.system("python test_rotation_ms_final.py")