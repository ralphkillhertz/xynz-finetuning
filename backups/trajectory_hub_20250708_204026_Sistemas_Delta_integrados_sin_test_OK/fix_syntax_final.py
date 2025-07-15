# === fix_syntax_final.py ===
# 🔧 Fix: Corregir f-string no cerrado definitivamente
# ⚡ Línea 798 de enhanced_trajectory_engine.py

def fix_syntax_error():
    """Corregir el f-string no cerrado en línea 798"""
    import os
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    print("🔧 FIX: F-string no cerrado en línea 798")
    print("=" * 60)
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Mostrar el problema
    print(f"📄 Línea 798 actual: {repr(lines[797])}")
    
    # Corregir línea 798
    # Basándome en el contexto, parece que debería ser un mensaje de confirmación
    lines[797] = '        print(f"✅ Rotación configurada para {configured}/{len(source_ids)} fuentes")\n'
    
    # Guardar archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"✅ Línea 798 corregida: {repr(lines[797])}")
    
    # Verificar sintaxis
    print("\n🔍 Verificando sintaxis...")
    import ast
    code = ''.join(lines)
    try:
        ast.parse(code)
        print("✅ Sintaxis correcta!")
        return True
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        print(f"   En línea {e.lineno}: {lines[e.lineno-1].strip()}")
        return False

if __name__ == "__main__":
    if fix_syntax_error():
        print("\n✅ Archivo corregido exitosamente")
        print("\n📋 Próximo paso: python test_individual_rotations.py")
    else:
        print("\n❌ Necesita más correcciones")