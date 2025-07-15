# === fix_def_indentation.py ===
# 🔧 Fix: Corregir indentación del def en línea 1010
# ⚡ ULTRA QUICK FIX

import os

# Leer archivo
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corregir línea 1010 - el def tiene demasiados espacios
if len(lines) > 1009:
    if lines[1009].strip().startswith('def update_with_deltas'):
        # Cambiar de 8 espacios a 4
        lines[1009] = lines[1009].replace('        def', '    def')
        print("✅ Línea 1010 corregida")

# Guardar
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("🚀 Ejecutando test...")
os.system("python test_rotation_ms_final.py")