#!/usr/bin/env python3
"""
🔧 Fix: Arregla el docstring con indentación excesiva
⚡ Línea 105: Tiene 26 espacios, debe tener 8
🎯 Solución: Corregir específicamente esa línea
"""

def fix_docstring_problem():
    """Arregla el problema específico del docstring"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    print("🔧 Arreglando problema específico del docstring...\n")
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    # Mostrar el problema
    print("📍 Problema identificado:")
    for i in range(103, 109):
        if i < len(lines):
            indent_count = len(lines[i]) - len(lines[i].lstrip())
            print(f"   Línea {i+1}: {indent_count} espacios - {repr(lines[i][:50])}")
    
    # Fix específico: línea 105 (índice 104)
    if 104 < len(lines):
        # Esta línea debe tener 8 espacios (contenido del método)
        content = lines[104].lstrip()
        lines[104] = '        ' + content  # 8 espacios
        print("\n✅ Línea 105 corregida a 8 espacios")
    
    # Verificar que las siguientes líneas también tengan 8 espacios
    for i in range(105, 111):
        if i < len(lines) and lines[i].strip():
            current_indent = len(lines[i]) - len(lines[i].lstrip())
            if current_indent != 8:
                content = lines[i].lstrip()
                lines[i] = '        ' + content  # 8 espacios
                print(f"✅ Línea {i+1} ajustada a 8 espacios")
    
    # Guardar
    with open(motion_file, 'w') as f:
        f.writelines(lines)
    
    print("\n📋 Resultado:")
    for i in range(103, 109):
        if i < len(lines):
            indent_count = len(lines[i]) - len(lines[i].lstrip())
            print(f"   Línea {i+1}: {indent_count} espacios - {repr(lines[i][:50])}")

def quick_verify():
    """Verificación rápida"""
    print("\n🧪 Verificando...")
    
    try:
        import ast
        with open("trajectory_hub/core/motion_components.py", 'r') as f:
            content = f.read()
        ast.parse(content)
        print("✅ ¡SINTAXIS CORRECTA!")
        return True
    except SyntaxError as e:
        print(f"❌ Error en línea {e.lineno}: {e.msg}")
        return False

def alternative_solution():
    """Si todo falla, restaurar del backup más reciente"""
    print("\n🔄 SOLUCIÓN ALTERNATIVA: Restaurar y re-aplicar deltas")
    
    commands = """
# 1. Restaurar del backup más reciente
cp trajectory_hub/core/motion_components.py.backup_20250707_164013 trajectory_hub/core/motion_components.py

# 2. Re-ejecutar la migración de deltas
python migrate_concentration_to_delta.py

# 3. Probar
python test_delta_final.py
"""
    
    print(commands)

if __name__ == "__main__":
    print("🔧 FIX ESPECÍFICO DEL DOCSTRING")
    print("=" * 60)
    
    fix_docstring_problem()
    
    if quick_verify():
        print("\n🎉 ¡PROBLEMA RESUELTO!")
        print("\nEjecuta ahora:")
        print("$ python test_delta_final.py")
    else:
        print("\n⚠️ El problema persiste")
        alternative_solution()