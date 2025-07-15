#!/usr/bin/env python3
"""
🔍 Analiza la estructura actual del engine
⚡ Determina exactamente dónde insertar los métodos
"""

def analyze_structure():
    """Analiza estructura y encuentra puntos de inserción"""
    
    print("🔍 ANALIZANDO ESTRUCTURA DE enhanced_trajectory_engine.py")
    print("=" * 60)
    
    engine_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(engine_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar métodos principales
    methods = []
    for i, line in enumerate(lines):
        if line.strip().startswith('def ') and not line.strip().startswith('def _'):
            method_name = line.strip().split('(')[0].replace('def ', '')
            indent = len(line) - len(line.lstrip())
            methods.append({
                'name': method_name,
                'line': i + 1,
                'indent': indent,
                'full_line': line.rstrip()
            })
    
    print("📋 MÉTODOS PÚBLICOS ENCONTRADOS:")
    for method in methods:
        print(f"   Línea {method['line']:4d}: {method['name']}()")
    
    # Buscar create_macro específicamente
    create_macro_line = -1
    create_macro_end = -1
    
    for i, line in enumerate(lines):
        if 'def create_macro' in line:
            create_macro_line = i
            # Buscar el final del método
            for j in range(i+1, len(lines)):
                # Si encontramos otro def al mismo nivel
                if lines[j].strip().startswith('def ') and len(lines[j]) - len(lines[j].lstrip()) <= 4:
                    create_macro_end = j
                    break
    
    print(f"\n📍 create_macro():")
    print(f"   Inicio: línea {create_macro_line + 1}")
    print(f"   Fin: línea {create_macro_end + 1}")
    print(f"   Tamaño: {create_macro_end - create_macro_line} líneas")
    
    # Verificar si hay espacio después
    if create_macro_end > 0 and create_macro_end < len(lines):
        print(f"\n📍 PUNTO DE INSERCIÓN IDEAL:")
        print(f"   Después de línea {create_macro_end}")
        print(f"   Siguiente método: {lines[create_macro_end].strip()}")
        
        # Mostrar contexto
        print(f"\n📄 CONTEXTO (líneas {create_macro_end-2} a {create_macro_end+3}):")
        for i in range(max(0, create_macro_end-2), min(len(lines), create_macro_end+3)):
            marker = ">>>" if i == create_macro_end else "   "
            print(f"{i+1:4d} {marker} {lines[i].rstrip()}")
    
    # Analizar estructura de datos
    print("\n📊 ESTRUCTURA DE DATOS:")
    has_macros = '_macros' in ''.join(lines)
    has_active_sources = '_active_sources' in ''.join(lines)
    has_source_ids = 'source_ids' in ''.join(lines)
    
    print(f"   _macros: {'✅' if has_macros else '❌'}")
    print(f"   _active_sources: {'✅' if has_active_sources else '❌'}")
    print(f"   source_ids: {'✅' if has_source_ids else '❌'}")
    
    # Buscar cómo se almacenan los macros
    print("\n🔍 ANÁLISIS DE ALMACENAMIENTO DE MACROS:")
    for i, line in enumerate(lines):
        if '_macros[' in line and '=' in line:
            print(f"   Línea {i+1}: {line.strip()}")
            # Ver las líneas alrededor
            if i > 0:
                print(f"   Contexto: {lines[i-1].strip()}")
    
    return {
        'insert_after_line': create_macro_end,
        'has_required_data': has_macros and has_active_sources,
        'methods_count': len(methods)
    }

if __name__ == "__main__":
    result = analyze_structure()
    
    print("\n📊 RESUMEN:")
    print(f"   Insertar después de línea: {result['insert_after_line']}")
    print(f"   Datos requeridos: {'✅' if result['has_required_data'] else '❌'}")
    print(f"   Total métodos públicos: {result['methods_count']}")
    
    if result['insert_after_line'] > 0 and result['has_required_data']:
        print("\n✅ LISTO PARA IMPLEMENTAR")
        print("🎯 Siguiente: Implementar list_macros() en la línea correcta")
    else:
        print("\n❌ Necesita más análisis")