# === fix_indentation_line_623.py ===
# 🔧 Fix: Corregir indentación línea 623
# ⚡ Impacto: CRÍTICO - Desbloquea sintaxis

import os

def fix_indentation():
    """Corrige el error de indentación en línea 623"""
    
    print("🔧 CORRIGIENDO INDENTACIÓN LÍNEA 623\n")
    
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo línea por línea
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 Total líneas: {len(lines)}")
    
    # Verificar contexto alrededor de línea 623
    if len(lines) >= 623:
        print("\n🔍 Contexto línea 623:")
        for i in range(max(0, 620), min(len(lines), 630)):
            indent = len(lines[i]) - len(lines[i].lstrip())
            print(f"  L{i+1} (indent={indent}): {lines[i].rstrip()}")
    
    # Corregir línea 623 (índice 622)
    if len(lines) > 622:
        line_622 = lines[622]
        
        # Si es la docstring, verificar que esté correctamente indentada
        if '"""' in line_622:
            # Ver la línea anterior para determinar indentación correcta
            if len(lines) > 621:
                prev_line = lines[621]
                if 'def ' in prev_line:
                    # Es el inicio de un método, necesita 8 espacios
                    lines[622] = '        """Configura rotación algorítmica para un macro alrededor de su centro"""\n'
                    print("\n✅ Línea 623 corregida con indentación de 8 espacios")
    
    # Guardar archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Archivo guardado")
    
    # Verificar sintaxis
    print("\n🧪 Verificando sintaxis...")
    import py_compile
    try:
        py_compile.compile(file_path, doraise=True)
        print("✅ Sintaxis correcta!")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Error persiste: {e}")
        
        # Si sigue fallando, intentar un fix más agresivo
        print("\n🔨 Aplicando fix agresivo...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el método set_macro_rotation y asegurar formato correcto
        import re
        pattern = r'(    def set_macro_rotation.*?)\n([^    ].*?)"""'
        replacement = r'\1\n        """'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return False

if __name__ == "__main__":
    if fix_indentation():
        print("\n🚀 Ejecutando test...")
        os.system("python test_macro_rotation_fixed.py")
    else:
        print("\n⚠️ Ejecutando segundo intento...")
        os.system("python fix_indentation_line_623.py")