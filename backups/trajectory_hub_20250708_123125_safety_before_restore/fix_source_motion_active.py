# === fix_source_motion_active.py ===
# 🔧 Fix: Añadir active_components a SourceMotion
# ⚡ INSTANT FIX

import os
import re

# Leer archivo
with open("trajectory_hub/core/motion_components.py", 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar clase SourceMotion
pattern = r'(class SourceMotion.*?def __init__.*?\n)(.*?)(?=\n    def |\n\nclass |\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    init_start = match.group(1)
    init_body = match.group(2)
    
    # Verificar si ya tiene active_components
    if 'self.active_components' not in init_body:
        print("🔧 Añadiendo active_components a SourceMotion...")
        
        # Buscar el final del __init__
        lines = init_body.split('\n')
        
        # Añadir active_components después del último self.
        last_self_line = -1
        for i, line in enumerate(lines):
            if 'self.' in line and '=' in line:
                last_self_line = i
        
        if last_self_line >= 0:
            # Insertar después de la última asignación
            lines.insert(last_self_line + 1, '        self.active_components: Dict[str, MotionComponent] = {}')
            init_body = '\n'.join(lines)
        else:
            # Añadir al principio
            init_body = '        self.active_components: Dict[str, MotionComponent] = {}\n' + init_body
        
        # Reconstruir
        new_content = content[:match.start()] + init_start + init_body + content[match.end(2):]
        
        # Guardar
        with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ active_components añadido")
    else:
        print("✅ active_components ya existe")
else:
    print("❌ No se encontró SourceMotion.__init__")
    print("🔧 Añadiendo manualmente...")
    
    # Buscar solo la clase
    class_pattern = r'class SourceMotion[^:]*:'
    class_match = re.search(class_pattern, content)
    
    if class_match:
        # Insertar justo después del docstring
        insert_pos = content.find('\n', class_match.end())
        if '"""' in content[class_match.end():class_match.end()+100]:
            # Buscar el cierre del docstring
            doc_end = content.find('"""', class_match.end()+3) + 3
            insert_pos = content.find('\n', doc_end)
        
        # Verificar si ya tiene __init__
        next_def = content.find('\n    def ', insert_pos)
        init_exists = content[insert_pos:next_def].find('def __init__') > 0 if next_def > 0 else False
        
        if not init_exists:
            # Añadir __init__ completo
            new_init = '''
    
    def __init__(self, state: MotionState):
        self.state = state
        self.active_components: Dict[str, MotionComponent] = {}
'''
            content = content[:insert_pos] + new_init + content[insert_pos:]
            
            with open("trajectory_hub/core/motion_components.py", 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ __init__ con active_components añadido")

print("\n🚀 Ejecutando test...")
os.system("python test_rotation_ms_final.py")