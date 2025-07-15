# === fix_line11_indent.py ===
# 🔧 Fix: Corregir indentación línea 11
# ⚡ ULTRA FAST

import os

with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corregir línea 11 - quitar espacios extra
if len(lines) > 10:
    lines[10] = lines[10].replace('            def', '    def')

# Guardar
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fixed line 11")
os.system("python test_rotation_ms_final.py")