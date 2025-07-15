# === fix_import_syntax_error.py ===
# 🔧 Fix: Corregir sintaxis del import
# ⚡ Impacto: CRÍTICO - Error de sintaxis

import os

def fix_import_syntax():
    """Corregir error de sintaxis en import"""
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("🔍 Buscando línea con error...")
    
    # Mostrar contexto alrededor de línea 21
    for i in range(max(0, 20-5), min(len(lines), 20+5)):
        print(f"{i+1:3d}: {lines[i].rstrip()}")
        if i == 20:  # Línea 21 (índice 20)
            print("     ^^^ ERROR AQUÍ")
    
    # Corregir línea 21
    if len(lines) > 20:
        bad_line = lines[20]
        print(f"\n❌ Línea problemática: {bad_line.strip()}")
        
        # Corregir el paréntesis mal puesto
        if '(,' in bad_line:
            # Quitar el paréntesis extra
            lines[20] = bad_line.replace('(,', '')
            print("✅ Quitado '(,' extra")
        elif 'import (' in bad_line:
            # Quitar paréntesis de apertura solo
            lines[20] = bad_line.replace('import (', 'import ')
            print("✅ Quitado '(' después de import")
        else:
            # Reescribir la línea completamente
            indent = len(bad_line) - len(bad_line.lstrip())
            lines[20] = ' ' * indent + 'from trajectory_hub.core.motion_components import MacroRotation\n'
            print("✅ Línea reescrita completamente")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Sintaxis corregida")
    return True

if __name__ == "__main__":
    print("🔧 Corrigiendo error de sintaxis en import...")
    
    if fix_import_syntax():
        print("\n✅ Archivo corregido")
        print("📝 Ejecuta: python test_macro_rotation_final_working.py")