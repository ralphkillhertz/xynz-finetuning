#!/usr/bin/env python3
"""
🔍 Analiza dónde insertar select_macro()
⚡ Busca list_macros() y determina posición
"""

def analyze_for_select():
    """Encuentra el mejor lugar para select_macro()"""
    
    print("🔍 ANALIZANDO PARA select_macro()")
    print("=" * 60)
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar list_macros
    list_macros_start = -1
    list_macros_end = -1
    
    for i, line in enumerate(lines):
        if 'def list_macros(self):' in line:
            list_macros_start = i
            print(f"✅ list_macros() encontrado en línea {i+1}")
            
            # Buscar el final
            indent_level = len(line) - len(line.lstrip())
            for j in range(i+1, len(lines)):
                current_line = lines[j]
                # Si encontramos algo con menor o igual indentación (no parte del método)
                if current_line.strip() and len(current_line) - len(current_line.lstrip()) <= indent_level:
                    list_macros_end = j - 1
                    break
            break
    
    if list_macros_start == -1:
        print("❌ No se encontró list_macros()")
        return None
    
    print(f"📍 list_macros() termina en línea {list_macros_end+1}")
    
    # Verificar qué hay después
    next_method_line = -1
    for i in range(list_macros_end+1, min(len(lines), list_macros_end+10)):
        if lines[i].strip().startswith('def '):
            next_method_line = i
            break
    
    if next_method_line > 0:
        print(f"📍 Siguiente método: línea {next_method_line+1} - {lines[next_method_line].strip()}")
    
    # Determinar punto de inserción
    insert_line = list_macros_end + 1
    
    # Si hay líneas en blanco, saltarlas
    while insert_line < len(lines) and lines[insert_line].strip() == '':
        insert_line += 1
    
    print(f"\n✅ PUNTO DE INSERCIÓN: después de línea {insert_line}")
    
    # Mostrar contexto
    print(f"\n📄 CONTEXTO (líneas {insert_line-3} a {insert_line+3}):")
    for i in range(max(0, insert_line-3), min(len(lines), insert_line+3)):
        marker = ">>>" if i == insert_line else "   "
        print(f"{i+1:4d} {marker} {lines[i].rstrip()}")
    
    # Verificar uso de select_macro en el código
    print("\n🔍 USOS EXISTENTES DE BÚSQUEDA DE MACROS:")
    for i, line in enumerate(lines):
        if "self._macros[" in line and "if" not in line:
            print(f"   Línea {i+1}: {line.strip()[:60]}...")
    
    return {
        'insert_after_line': insert_line,
        'list_macros_ends': list_macros_end,
        'ready': True
    }

if __name__ == "__main__":
    result = analyze_for_select()
    
    if result and result['ready']:
        print("\n✅ LISTO PARA IMPLEMENTAR select_macro()")
        print(f"🎯 Insertar después de línea {result['insert_after_line']}")
    else:
        print("\n❌ Necesita revisión manual")