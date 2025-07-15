#!/usr/bin/env python3
"""
🔍 Analiza los métodos de macros existentes en el Controller
⚡ Ver qué hacen y cómo integrar los nuevos
"""

def analyze_macro_methods():
    """Analiza implementación actual de macros"""
    
    print("🔍 ANÁLISIS DE MÉTODOS DE MACROS EXISTENTES")
    print("=" * 60)
    
    controller_path = 'trajectory_hub/interface/interactive_controller.py'
    
    with open(controller_path, 'r') as f:
        lines = f.readlines()
    
    # Métodos a buscar
    methods_to_analyze = [
        'list_active_macros',
        'show_macro_info',
        'create_macro_wizard',
        '_list_active_macros',
        '_show_macro_info'
    ]
    
    for method_name in methods_to_analyze:
        print(f"\n📋 ANALIZANDO: {method_name}()")
        print("-" * 40)
        
        # Buscar el método
        method_start = -1
        for i, line in enumerate(lines):
            if f'def {method_name}' in line:
                method_start = i
                break
        
        if method_start == -1:
            print(f"   ❌ No encontrado")
            continue
        
        print(f"   📍 Encontrado en línea {method_start + 1}")
        
        # Extraer las primeras líneas del método
        indent_level = len(lines[method_start]) - len(lines[method_start].lstrip())
        method_lines = []
        
        for i in range(method_start, min(method_start + 20, len(lines))):
            line = lines[i]
            # Si es parte del método
            if i == method_start or (line.strip() and len(line) - len(line.lstrip()) > indent_level):
                method_lines.append(line.rstrip())
            elif line.strip() and len(line) - len(line.lstrip()) <= indent_level:
                break
        
        # Mostrar contenido
        print("   CONTENIDO:")
        for line in method_lines[:10]:  # Primeras 10 líneas
            print(f"   {line}")
        
        # Buscar qué usa
        method_content = '\n'.join(method_lines)
        if 'self.engine._macros' in method_content:
            print("   🔧 USA: self.engine._macros directamente")
        if 'self.engine.list_macros' in method_content:
            print("   🔧 USA: self.engine.list_macros()")
        if 'print(' in method_content:
            print("   🔧 USA: print() para mostrar")
    
    # Buscar dónde se usan estos métodos
    print("\n🔍 USO DE MÉTODOS:")
    for method_name in ['list_active_macros', '_list_active_macros', 'show_macro_info', '_show_macro_info']:
        uses = []
        for i, line in enumerate(lines):
            if method_name in line and 'def ' not in line:
                uses.append(f"   Línea {i+1}: {line.strip()[:60]}...")
        
        if uses:
            print(f"\n{method_name} se usa en:")
            for use in uses[:5]:
                print(use)
    
    # Buscar menú donde están
    print("\n🔍 UBICACIÓN EN MENÚS:")
    in_menu = None
    for i, line in enumerate(lines):
        if 'def _show_' in line and '_menu(' in line:
            in_menu = line.strip()
        elif in_menu and ('list_active_macros' in line or 'show_macro_info' in line):
            print(f"   {in_menu}")
            print(f"   └─ Línea {i+1}: {line.strip()}")
    
    # Ver si hay opción de delete
    print("\n🔍 BÚSQUEDA DE DELETE:")
    delete_found = False
    for i, line in enumerate(lines):
        if 'delete' in line.lower() and 'macro' in line.lower():
            print(f"   Línea {i+1}: {line.strip()}")
            delete_found = True
    
    if not delete_found:
        print("   ❌ No hay funcionalidad de delete macro")
    
    return {
        'has_list': 'list_active_macros' in '\n'.join(lines),
        'has_delete': delete_found,
        'uses_new_methods': 'self.engine.list_macros' in '\n'.join(lines)
    }

if __name__ == "__main__":
    result = analyze_macro_methods()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    print(f"   Tiene list_active_macros: {'✅' if result['has_list'] else '❌'}")
    print(f"   Tiene delete_macro: {'✅' if result['has_delete'] else '❌'}")
    print(f"   Usa nuevos métodos: {'✅' if result['uses_new_methods'] else '❌'}")
    
    print("\n🎯 ESTRATEGIA RECOMENDADA:")
    if not result['uses_new_methods']:
        print("   1. Actualizar list_active_macros para usar engine.list_macros()")
        print("   2. Añadir opción de delete_macro al menú")
        print("   3. Integrar select_macro para selección mejorada")
    else:
        print("   ✅ Ya usa los nuevos métodos")