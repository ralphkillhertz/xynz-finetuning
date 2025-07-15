# === fix_indentation_line1011.py ===
# 🔧 Fix: Corregir indentación línea 1011
# ⚡ INSTANT FIX

import os

# Leer archivo
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Verificar línea 1011
if len(lines) > 1010:
    print(f"📋 Línea 1010: {repr(lines[1009][:60])}")
    print(f"📋 Línea 1011: {repr(lines[1010][:60])}")
    
    # Si la línea 1011 tiene un docstring mal indentado
    if '"""' in lines[1010] and not lines[1010].startswith('        '):
        lines[1010] = '        ' + lines[1010].lstrip()
        print("✅ Indentación corregida")
        
        # Guardar
        with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
            f.writelines(lines)

# Ahora arreglar todo el método si es necesario
print("\n🔧 Verificando estructura del método...")

with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar el método update_with_deltas mal formateado
import re
pattern = r'def update_with_deltas\(.*?\).*?:\n([ ]*""".*?""")'
match = re.search(pattern, content, re.DOTALL)

if match:
    docstring = match.group(1)
    if not docstring.startswith('        '):
        print("🔧 Arreglando indentación del método completo...")
        
        # Buscar el método completo
        start = content.find('def update_with_deltas')
        if start > 0:
            # Verificar indentación previa
            prev_line_start = content.rfind('\n', 0, start)
            indent = len(content[prev_line_start+1:start]) - len(content[prev_line_start+1:start].lstrip())
            
            # Buscar el final del método
            next_def = content.find('\n    def ', start + 1)
            next_class = content.find('\nclass ', start + 1)
            end = min(x for x in [next_def, next_class, len(content)] if x > start)
            
            # Extraer método
            method = content[start:end]
            
            # Re-indentar correctamente
            lines = method.split('\n')
            fixed_lines = []
            for line in lines:
                if line.strip():
                    if line.strip().startswith('def '):
                        fixed_lines.append('    ' + line.strip())
                    else:
                        fixed_lines.append('        ' + line.strip())
                else:
                    fixed_lines.append('')
            
            # Reemplazar
            content = content[:start] + '\n'.join(fixed_lines) + content[end:]
            
            # Guardar
            with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Método re-indentado")

print("\n🚀 Ejecutando test...")
os.system("python test_rotation_ms_final.py")