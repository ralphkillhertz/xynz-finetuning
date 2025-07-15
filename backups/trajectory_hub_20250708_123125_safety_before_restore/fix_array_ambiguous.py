# === fix_array_ambiguous.py ===
# 🔧 Fix: Corregir error "array truth value ambiguous"
# ⚡ FINAL TURBO FIX

import os
import re

# Leer archivo
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()

print("🔍 Buscando método update_with_deltas con problema de array...")

# Buscar el método update_with_deltas
pattern = r'def update_with_deltas\(.*?\).*?:(.*?)(?=\n    def |\nclass |\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    method_content = match.group(0)
    
    # Buscar la línea problemática
    if 'if delta and' in method_content:
        print("✅ Encontrado, corrigiendo condición...")
        
        # Reemplazar la condición problemática
        # OLD: if delta and (np.any(delta.position != 0) or ...
        # NEW: if delta is not None and (np.any(delta.position != 0) or ...
        
        fixed_method = re.sub(
            r'if delta and \(',
            'if delta is not None and (',
            method_content
        )
        
        # También asegurar que la comparación con arrays sea correcta
        fixed_method = re.sub(
            r'delta\.position != 0',
            'delta.position != 0',
            fixed_method
        )
        
        # Reemplazar en el contenido
        content = content.replace(method_content, fixed_method)
        
        print("✅ Condición corregida")

# Guardar
with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Archivo actualizado")
print("🚀 Ejecutando test final...")
os.system("python test_rotation_ms_final.py")