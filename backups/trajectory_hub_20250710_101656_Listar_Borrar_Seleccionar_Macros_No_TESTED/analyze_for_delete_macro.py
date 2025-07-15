#!/usr/bin/env python3
"""
🔍 Analiza dónde insertar delete_macro() y cómo eliminar sources
⚡ Busca select_macro() y analiza eliminación de sources
"""

def analyze_for_delete():
    """Encuentra el mejor lugar para delete_macro() y analiza eliminación"""
    
    print("🔍 ANALIZANDO PARA delete_macro()")
    print("=" * 60)
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar select_macro
    select_macro_start = -1
    select_macro_end = -1
    
    for i, line in enumerate(lines):
        if 'def select_macro(self' in line:
            select_macro_start = i
            print(f"✅ select_macro() encontrado en línea {i+1}")
            
            # Buscar el final
            indent_level = len(line) - len(line.lstrip())
            for j in range(i+1, len(lines)):
                current_line = lines[j]
                if current_line.strip() and len(current_line) - len(current_line.lstrip()) <= indent_level:
                    select_macro_end = j - 1
                    break
            break
    
    print(f"📍 select_macro() termina en línea {select_macro_end+1}")
    
    # Buscar cómo se maneja _active_sources
    print("\n🔍 ANÁLISIS DE _active_sources:")
    active_sources_usage = []
    for i, line in enumerate(lines):
        if '_active_sources' in line:
            if 'add(' in line or 'remove(' in line or 'discard(' in line:
                active_sources_usage.append(f"   Línea {i+1}: {line.strip()}")
    
    if active_sources_usage:
        print("   Operaciones encontradas:")
        for usage in active_sources_usage[:5]:  # Mostrar primeras 5
            print(usage)
    
    # Buscar si _active_sources es un set o lista
    print("\n🔍 TIPO DE _active_sources:")
    for i, line in enumerate(lines):
        if '_active_sources = ' in line or '_active_sources: ' in line:
            print(f"   Línea {i+1}: {line.strip()}")
            if 'set()' in line:
                print("   ✅ Es un SET")
            elif '[]' in line:
                print("   ✅ Es una LISTA")
    
    # Buscar cómo se eliminan macros existentes
    print("\n🔍 ELIMINACIÓN DE MACROS/SOURCES:")
    for i, line in enumerate(lines):
        if 'del ' in line and '_macros' in line:
            print(f"   Línea {i+1}: {line.strip()}")
    
    # Punto de inserción
    insert_line = select_macro_end + 1
    while insert_line < len(lines) and lines[insert_line].strip() == '':
        insert_line += 1
    
    print(f"\n✅ PUNTO DE INSERCIÓN: después de línea {insert_line}")
    
    # Mostrar contexto
    print(f"\n📄 CONTEXTO (líneas {insert_line-3} a {insert_line+3}):")
    for i in range(max(0, insert_line-3), min(len(lines), insert_line+3)):
        marker = ">>>" if i == insert_line else "   "
        print(f"{i+1:4d} {marker} {lines[i].rstrip()}")
    
    # Buscar si hay método de eliminación de sources
    print("\n🔍 MÉTODOS DE ELIMINACIÓN EXISTENTES:")
    for i, line in enumerate(lines):
        if 'def ' in line and ('delete' in line.lower() or 'remove' in line.lower()):
            print(f"   Línea {i+1}: {line.strip()}")
    
    return {
        'insert_after_line': insert_line,
        'active_sources_is_set': True,  # Basado en análisis previo
        'ready': True
    }

if __name__ == "__main__":
    result = analyze_for_delete()
    
    if result and result['ready']:
        print("\n✅ LISTO PARA IMPLEMENTAR delete_macro()")
        print("📋 INFORMACIÓN CLAVE:")
        print("   - _active_sources parece ser un SET")
        print("   - Usar discard() para eliminar sources")
        print("   - Eliminar con del self._macros[key]")
        print(f"\n🎯 Insertar después de línea {result['insert_after_line']}")
    else:
        print("\n❌ Necesita revisión manual")