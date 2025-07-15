# === fix_motion_delta_source_id.py ===
# 🔧 Fix: Añadir source_id a MotionDelta
# ⚡ Impacto: CRÍTICO - Bloquea sistema de deltas

import os
import re

def fix_motion_delta():
    """Añade source_id a la clase MotionDelta"""
    
    file_path = "trajectory_hub/core/motion_components.py"
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la clase MotionDelta
    pattern = r'(class MotionDelta:.*?)(\n    def __init__\(self\):.*?\n        )(.*?)(\n\n|\nclass)'
    
    def replacer(match):
        class_def = match.group(1)
        init_def = match.group(2)
        init_body = match.group(3)
        next_section = match.group(4)
        
        # Añadir source_id al __init__
        if 'source_id' not in init_body:
            new_init_body = 'self.source_id = None\n        ' + init_body
        else:
            new_init_body = init_body
            
        return class_def + init_def + new_init_body + next_section
    
    content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    
    # También actualizar calculate_delta para que incluya source_id
    # Buscar todos los return MotionDelta() y actualizarlos
    def update_motion_delta_creation(match_text):
        # Patrón para encontrar creación de MotionDelta
        delta_pattern = r'delta = MotionDelta\(\)'
        replacement = 'delta = MotionDelta()\n        delta.source_id = state.source_id'
        return re.sub(delta_pattern, replacement, match_text)
    
    # Aplicar a cada método calculate_delta
    methods = re.findall(r'def calculate_delta\(.*?\n(?:.*?\n)*?return delta', content, re.DOTALL)
    for method in methods:
        updated_method = update_motion_delta_creation(method)
        if updated_method != method:
            content = content.replace(method, updated_method)
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ MotionDelta actualizado con source_id")
    print("✅ Métodos calculate_delta actualizados")
    
if __name__ == "__main__":
    fix_motion_delta()
    print("\n🚀 Ejecutando test final...")
    os.system("python test_macro_final_working.py")