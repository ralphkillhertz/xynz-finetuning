# === fix_macro_rotation_inheritance.py ===
# 🔧 Fix: Corregir herencia de MacroRotation
# ⚡ Impacto: CRÍTICO - Desbloquea rotaciones

import os
import re

def fix_inheritance():
    """Arregla la herencia de MacroRotation"""
    
    file_path = "trajectory_hub/core/motion_components.py"
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar qué clases base existen
    print("🔍 Buscando clases base disponibles...")
    
    # Buscar clases que podrían ser la base
    if "class MotionComponent" in content:
        print("✅ MotionComponent encontrado")
        base_class = "MotionComponent"
    elif "@dataclass" in content and "class MotionState" in content:
        print("📦 Usando estructura dataclass")
        base_class = None
    else:
        print("⚠️ No se encontró clase base")
        base_class = None
    
    # Opción 1: Si no hay MotionComponent, hacer MacroRotation independiente
    if base_class is None:
        # Reemplazar la definición de MacroRotation
        old_pattern = r'class MacroRotation\(MotionComponent\):'
        new_pattern = 'class MacroRotation:'
        content = content.replace(old_pattern, new_pattern)
        
        # También quitar super().__init__() si existe
        content = content.replace("super().__init__()", "pass  # No parent class")
        
        print("✅ MacroRotation ahora es clase independiente")
    else:
        # Mover MacroRotation después de MotionComponent
        # Extraer la clase MacroRotation
        macro_rotation_match = re.search(
            r'(class MacroRotation.*?)(?=\nclass|\n@|\Z)', 
            content, 
            re.DOTALL
        )
        
        if macro_rotation_match:
            macro_rotation_code = macro_rotation_match.group(1)
            # Eliminar de su posición actual
            content = content.replace(macro_rotation_code, '')
            
            # Insertar después de MotionComponent o al final
            insert_after = "class MotionState:"
            insert_pos = content.find(insert_after)
            if insert_pos > 0:
                content = content[:insert_pos] + macro_rotation_code + "\n\n" + content[insert_pos:]
                print("✅ MacroRotation movido a posición correcta")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Ahora arreglar el import en el engine
    print("\n🔧 Arreglando imports en engine...")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    with open(engine_path, 'r', encoding='utf-8') as f:
        engine_content = f.read()
    
    # Buscar la línea de imports correcta
    import_pattern = r'from \.motion_components import .*'
    match = re.search(import_pattern, engine_content)
    
    if match and "MacroRotation" not in match.group(0):
        old_import = match.group(0)
        # Añadir MacroRotation al final
        if old_import.endswith(')'):
            new_import = old_import[:-1] + ", MacroRotation)"
        else:
            new_import = old_import + ", MacroRotation"
        
        engine_content = engine_content.replace(old_import, new_import)
        print("✅ Import de MacroRotation añadido")
    
    # Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(engine_content)
    
    print("\n✅ Herencia y imports corregidos")

if __name__ == "__main__":
    fix_inheritance()
    print("\n🚀 Ejecutando test...")
    os.system("python test_macro_rotation.py")