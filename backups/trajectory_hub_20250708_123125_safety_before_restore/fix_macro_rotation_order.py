# === fix_macro_rotation_order.py ===
# 🔧 Fix: Mover MacroRotation después de MotionComponent
# ⚡ Impacto: CRÍTICO - Resuelve orden de definición

import os
import re

def fix_class_order():
    """Mueve MacroRotation después de MotionComponent"""
    
    file_path = "trajectory_hub/core/motion_components.py"
    
    print("🔧 Reordenando clases en motion_components.py...")
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Extraer la clase MacroRotation completa
    macro_rotation_pattern = r'(class MacroRotation.*?)(?=\n(?:class|@dataclass|$))'
    macro_match = re.search(macro_rotation_pattern, content, re.DOTALL)
    
    if not macro_match:
        print("❌ No se encontró MacroRotation")
        return
    
    macro_rotation_code = macro_match.group(1)
    print(f"✅ MacroRotation extraído ({len(macro_rotation_code)} caracteres)")
    
    # 2. Eliminar MacroRotation de su posición actual
    content = content.replace(macro_rotation_code, '')
    
    # 3. Buscar MotionComponent y encontrar dónde termina
    motion_component_pattern = r'(class MotionComponent.*?)(?=\n(?:class|@dataclass|$))'
    motion_match = re.search(motion_component_pattern, content, re.DOTALL)
    
    if motion_match:
        # Insertar después de MotionComponent
        end_pos = motion_match.end()
        content = content[:end_pos] + "\n\n" + macro_rotation_code + "\n" + content[end_pos:]
        print("✅ MacroRotation movido después de MotionComponent")
    else:
        print("⚠️ No se encontró MotionComponent, insertando al final")
        content = content + "\n\n" + macro_rotation_code
    
    # 4. Guardar archivo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo guardado con el orden correcto")
    
    # 5. Verificar sintaxis
    try:
        import py_compile
        py_compile.compile(file_path, doraise=True)
        print("✅ Sintaxis verificada correctamente")
    except Exception as e:
        print(f"❌ Error de sintaxis: {e}")

if __name__ == "__main__":
    fix_class_order()
    print("\n🚀 Ejecutando test...")
    os.system("python test_macro_rotation.py")