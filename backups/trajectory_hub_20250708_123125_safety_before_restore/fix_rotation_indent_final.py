# === fix_rotation_indent_final.py ===
# 🔧 Fix: Solución definitiva para indentación
# ⚡ Impacto: CRÍTICO - Rompe el bucle

import os

def fix_indent_final():
    """Fix definitivo para el problema de indentación"""
    
    print("🔧 FIX DEFINITIVO DE INDENTACIÓN\n")
    
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer líneas
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # El problema: la docstring en línea 623 necesita 12 espacios, no 8
    if len(lines) > 622:
        # Línea 622 tiene el def (con 8 espacios)
        # Línea 623 debe tener la docstring con 12 espacios
        if 'def set_macro_rotation' in lines[621]:
            lines[622] = '            """Configura rotación algorítmica para un macro alrededor de su centro"""\n'
            print("✅ Docstring corregida con 12 espacios")
        
        # También corregir las líneas siguientes que puedan tener indentación incorrecta
        for i in range(623, min(len(lines), 650)):
            line = lines[i].rstrip()
            if line and not line.startswith('        '):
                # Si la línea tiene contenido pero menos de 8 espacios, corregir
                stripped = line.lstrip()
                if stripped and not stripped.startswith('#'):
                    # Es código, debe tener al menos 12 espacios
                    lines[i] = '            ' + stripped + '\n'
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Archivo guardado")
    
    # Verificar líneas alrededor de 623
    print("\n📋 Verificación:")
    for i in range(620, min(len(lines), 635)):
        if i < len(lines):
            indent = len(lines[i]) - len(lines[i].lstrip())
            print(f"L{i+1} (indent={indent}): {lines[i].rstrip()[:60]}")

if __name__ == "__main__":
    fix_indent_final()
    print("\n🚀 Ejecutando test de rotación...")
    os.system("python test_macro_rotation_fixed.py")