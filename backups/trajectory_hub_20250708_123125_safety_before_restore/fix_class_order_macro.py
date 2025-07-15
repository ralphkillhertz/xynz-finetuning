# === fix_class_order_macro.py ===
# 🔧 Fix: Mover MacroRotation al lugar correcto
# ⚡ TURBO FIX

import os
import re

# Leer archivo
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Extraer MacroRotation (está al principio incorrectamente)
macro_pattern = r'^class MacroRotation.*?(?=\nclass |\n@|\Z)'
macro_match = re.search(macro_pattern, content, re.MULTILINE | re.DOTALL)

if macro_match:
    macro_class = macro_match.group(0)
    # Eliminar del principio
    content = content.replace(macro_class, '', 1)
    
    # Buscar donde insertarla (después de MotionComponent)
    # Buscar el final de la clase IndividualTrajectory o MacroTrajectory
    insert_pattern = r'(class MacroTrajectory.*?(?=\nclass |\n@|\Z))'
    insert_match = re.search(insert_pattern, content, re.DOTALL)
    
    if insert_match:
        # Insertar después de MacroTrajectory
        insert_pos = insert_match.end()
        content = content[:insert_pos] + '\n\n' + macro_class + content[insert_pos:]
    else:
        # Si no encuentra, buscar otro lugar
        insert_pattern2 = r'(class IndividualTrajectory.*?(?=\nclass |\n@|\Z))'
        insert_match2 = re.search(insert_pattern2, content, re.DOTALL)
        if insert_match2:
            insert_pos = insert_match2.end()
            content = content[:insert_pos] + '\n\n' + macro_class + content[insert_pos:]

# Limpiar líneas vacías extras
content = re.sub(r'\n\n\n+', '\n\n', content)

# Guardar
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ MacroRotation movida al lugar correcto")
os.system("python test_rotation_ms_final.py")