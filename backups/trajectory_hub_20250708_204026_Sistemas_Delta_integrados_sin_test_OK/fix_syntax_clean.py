# === fix_syntax_clean.py ===
# 🔧 Fix: Limpiar error de sintaxis y líneas duplicadas
# ⚡ Líneas alrededor de 798

def fix_syntax_clean():
    """Corregir f-string y limpiar líneas problemáticas"""
    import os
    
    file_path = os.path.join("trajectory_hub", "core", "enhanced_trajectory_engine.py")
    
    print("🔧 FIX: Limpiando errores de sintaxis")
    print("=" * 60)
    
    # Leer archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Mostrar contexto
    print("📄 Contexto líneas 795-805:")
    for i in range(795, min(805, len(lines))):
        print(f"   {i}: {repr(lines[i-1])}")
    
    # Corregir línea 798 y eliminar la 799 si es duplicada
    lines[797] = '        print(f"Rotacion configurada para {configured}/{len(source_ids)} fuentes")\n'
    
    # Si la línea 799 contiene el texto duplicado, eliminarla
    if len(lines) > 798 and "Rotación configurada" in lines[798]:
        print(f"\n🗑️ Eliminando línea duplicada 799: {repr(lines[798])}")
        del lines[798]
    
    # Guardar archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo corregido")
    
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
        if e.lineno:
            print(f"   En línea {e.lineno}: {lines[e.lineno-1].strip()}")
        return False

if __name__ == "__main__":
    if fix_syntax_clean():
        print("\n✅ Archivo limpiado exitosamente")
        print("\n📋 Próximo paso: python test_individual_rotations.py")
    else:
        print("\n❌ Aún hay errores")