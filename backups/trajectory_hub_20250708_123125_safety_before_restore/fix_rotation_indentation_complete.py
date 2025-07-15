# === fix_rotation_indentation_complete.py ===
# 🔧 Fix: Corregir toda la indentación del método set_macro_rotation
# ⚡ Impacto: CRÍTICO - Arregla sintaxis

import os
import re

def fix_rotation_indentation():
    """Corrige completamente la indentación de set_macro_rotation"""
    
    print("🔧 FIX COMPLETO DE INDENTACIÓN\n")
    
    engine_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el método completo y corregir su indentación
    print("🔍 Buscando set_macro_rotation...")
    
    # Patrón para encontrar el método mal indentado
    pattern = r'(\n)(        def set_macro_rotation.*?)(\n    def |\n\nclass |\Z)'
    
    def fix_method_indent(match):
        newline = match.group(1)
        method_content = match.group(2)
        next_section = match.group(3)
        
        # Quitar 4 espacios extra de cada línea
        lines = method_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.strip():  # Si la línea tiene contenido
                # Quitar 4 espacios del inicio si los tiene
                if line.startswith('        '):
                    fixed_lines.append(line[4:])
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        fixed_method = '\n'.join(fixed_lines)
        print("✅ Indentación corregida")
        
        return newline + fixed_method + next_section
    
    # Aplicar corrección
    content = re.sub(pattern, fix_method_indent, content, flags=re.DOTALL)
    
    # Guardar
    with open(engine_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo guardado")
    
    # Verificar sintaxis
    print("\n🧪 Verificando sintaxis...")
    import py_compile
    try:
        py_compile.compile(engine_path, doraise=True)
        print("✅ ¡Sintaxis correcta!")
    except py_compile.PyCompileError as e:
        print(f"❌ Error de sintaxis: {e}")
        
        # Si sigue fallando, hacer un fix más agresivo
        print("\n🔨 Aplicando fix más agresivo...")
        
        with open(engine_path, 'r') as f:
            lines = f.readlines()
        
        # Buscar la línea del def set_macro_rotation
        in_rotation_method = False
        fixed_lines = []
        
        for i, line in enumerate(lines):
            if 'def set_macro_rotation' in line:
                in_rotation_method = True
                # Asegurar que empiece con 4 espacios
                fixed_lines.append('    def set_macro_rotation(self, macro_name: str, speed_x: float = 0, speed_y: float = 0, speed_z: float = 0):\n')
            elif in_rotation_method and line.strip() and not line.startswith('    '):
                # Si estamos en el método y la línea no está bien indentada
                if line.strip().startswith('def '):
                    # Es otro método, terminamos
                    in_rotation_method = False
                    fixed_lines.append(line)
                else:
                    # Arreglar indentación (8 espacios para contenido del método)
                    fixed_lines.append('        ' + line.strip() + '\n')
            else:
                fixed_lines.append(line)
        
        # Guardar versión corregida
        with open(engine_path, 'w') as f:
            f.writelines(fixed_lines)
        
        print("✅ Fix agresivo aplicado")

if __name__ == "__main__":
    fix_rotation_indentation()
    print("\n🚀 Ejecutando test final...")
    os.system("python test_rotation_ms_final.py")