# === fix_indent_2415_robust.py ===
# 🔧 Fix: Corregir indentación línea 2415 de forma robusta
# ⚡ Impacto: CRÍTICO - Bloquea todo

import os

def fix_indentation():
    """Corrige el problema de indentación en línea 2415"""
    
    file_path = "trajectory_hub/core/enhanced_trajectory_engine.py"
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📄 Total líneas: {len(lines)}")
    
    # Examinar contexto alrededor de línea 2415
    if len(lines) >= 2415:
        print("\n🔍 Contexto línea 2415:")
        for i in range(max(0, 2410), min(len(lines), 2420)):
            indent = len(lines[i]) - len(lines[i].lstrip())
            print(f"  L{i+1} (indent={indent}): {lines[i].rstrip()}")
    
    # Buscar el problema específico
    problem_line = 2414  # índice 0-based
    if problem_line < len(lines):
        # Ver línea anterior para determinar indentación correcta
        prev_line = lines[problem_line - 1] if problem_line > 0 else ""
        prev_indent = len(prev_line) - len(prev_line.lstrip())
        
        # Si la línea anterior termina en ':' necesitamos más indentación
        if prev_line.rstrip().endswith(':'):
            correct_indent = prev_indent + 4
        else:
            correct_indent = prev_indent
        
        # Corregir la línea problemática
        if problem_line < len(lines):
            current_line = lines[problem_line].lstrip()
            lines[problem_line] = ' ' * correct_indent + current_line
            print(f"\n✅ Línea 2415 corregida con indentación: {correct_indent}")
    
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
        print(f"❌ Error de sintaxis persiste: {e}")
        return False

if __name__ == "__main__":
    if fix_indentation():
        print("\n🚀 Ejecutando test final...")
        os.system("python test_macro_final_working.py")
    else:
        print("\n⚠️ Necesita más correcciones")