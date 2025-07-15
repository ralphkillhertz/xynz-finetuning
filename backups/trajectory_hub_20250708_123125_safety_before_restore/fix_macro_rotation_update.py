# === fix_macro_rotation_update.py ===
# 🔧 Fix: Añadir método update a MacroRotation
# ⚡ Impacto: CRÍTICO - Completa la clase abstracta

import os
import re

def fix_macro_rotation_update():
    """Añade el método update a la clase MacroRotation"""
    
    print("🔧 AÑADIENDO MÉTODO update A MacroRotation\n")
    
    motion_path = "trajectory_hub/core/motion_components.py"
    
    # Leer archivo
    with open(motion_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Buscando clase MacroRotation...")
    
    # Buscar la clase MacroRotation
    class_pattern = r'(class MacroRotation.*?)((?=\nclass |\n@dataclass|\Z))'
    match = re.search(class_pattern, content, re.DOTALL)
    
    if match:
        class_content = match.group(1)
        next_section = match.group(2)
        
        # Verificar si ya tiene método update
        if 'def update(' not in class_content:
            print("❌ Método update no encontrado, añadiendo...")
            
            # Añadir método update antes del final de la clase
            update_method = '''
    def update(self, current_time: float, dt: float, state: MotionState) -> MotionState:
        """Actualiza el estado aplicando la rotación (requerido por MotionComponent)"""
        # El trabajo real se hace en calculate_delta
        # Este método solo retorna el estado sin cambios
        # ya que las modificaciones se aplican via deltas
        return state
'''
            
            # Insertar antes del final de la clase
            # Buscar el último método
            last_method_end = class_content.rfind('\n    def ')
            if last_method_end > 0:
                # Buscar el final de ese método
                lines = class_content[last_method_end:].split('\n')
                insert_pos = last_method_end
                
                # Buscar donde termina el último método
                indent_level = 0
                for i, line in enumerate(lines[1:], 1):  # Saltar la línea del def
                    if line.strip() and not line.startswith('        '):
                        # Encontramos algo con menos indentación
                        insert_pos = last_method_end + sum(len(l) + 1 for l in lines[:i])
                        break
                else:
                    # Llegamos al final
                    insert_pos = len(class_content)
                
                # Insertar el método update
                class_content = class_content[:insert_pos].rstrip() + '\n' + update_method + '\n' + class_content[insert_pos:]
            else:
                # No hay métodos, añadir al final
                class_content = class_content.rstrip() + update_method
            
            print("✅ Método update añadido")
        else:
            print("✅ Método update ya existe")
        
        # Reconstruir contenido
        content = content[:match.start()] + class_content + next_section + content[match.end():]
    else:
        print("❌ No se encontró la clase MacroRotation")
    
    # Guardar
    with open(motion_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Archivo actualizado")
    
    # Verificar sintaxis
    print("\n🧪 Verificando sintaxis...")
    import py_compile
    try:
        py_compile.compile(motion_path, doraise=True)
        print("✅ Sintaxis correcta")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_macro_rotation_update()
    print("\n🚀 Ejecutando test final...")
    os.system("python test_rotation_ms_final.py")