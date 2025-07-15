#!/usr/bin/env python3
"""
🔍 Verifica si el Controller tiene menú de gestión de macros
⚡ Analiza la estructura actual del menú
"""

def check_controller():
    """Verifica el estado actual del Interactive Controller"""
    
    print("🔍 VERIFICANDO INTERACTIVE CONTROLLER")
    print("=" * 60)
    
    controller_path = 'trajectory_hub/interface/interactive_controller.py'
    
    with open(controller_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Buscar menú principal
    print("📋 OPCIONES DEL MENÚ PRINCIPAL:")
    in_main_menu = False
    menu_options = []
    
    for i, line in enumerate(lines):
        if 'show_main_menu' in line:
            in_main_menu = True
        elif in_main_menu and '"' in line and '":' in line:
            # Extraer opción del menú
            if 'options = {' not in line:
                option = line.strip()
                menu_options.append(option)
                print(f"   {option}")
        elif in_main_menu and 'def ' in line:
            break
    
    # Verificar si existe gestión de macros
    has_macro_menu = False
    macro_keywords = ['manage_macros', 'show_macro', 'delete_macro', 'list_macro']
    
    for keyword in macro_keywords:
        if keyword in content.lower():
            has_macro_menu = True
            break
    
    print(f"\n📊 ANÁLISIS:")
    print(f"   Opciones encontradas: {len(menu_options)}")
    print(f"   Gestión de macros: {'✅ SÍ' if has_macro_menu else '❌ NO'}")
    
    # Buscar métodos relacionados con macros
    print("\n🔍 MÉTODOS RELACIONADOS CON MACROS:")
    methods_found = []
    for i, line in enumerate(lines):
        if 'def ' in line and 'macro' in line.lower():
            method_name = line.strip()
            methods_found.append(f"   Línea {i+1}: {method_name}")
    
    if methods_found:
        for method in methods_found[:10]:  # Primeros 10
            print(method)
    else:
        print("   ❌ No se encontraron métodos de gestión de macros")
    
    # Buscar última opción del menú
    last_option = 0
    for option in menu_options:
        if '"' in option:
            try:
                num = int(option.split('"')[1])
                if num > last_option:
                    last_option = num
            except:
                pass
    
    print(f"\n📊 RESUMEN:")
    print(f"   Última opción del menú: {last_option}")
    print(f"   Siguiente opción disponible: {last_option + 1}")
    
    return {
        'has_macro_menu': has_macro_menu,
        'last_menu_option': last_option,
        'next_option': last_option + 1
    }

if __name__ == "__main__":
    result = check_controller()
    
    if not result['has_macro_menu']:
        print("\n❌ NO HAY MENÚ DE GESTIÓN DE MACROS")
        print(f"🎯 Se puede añadir como opción {result['next_option']}")
        print("\n📋 OPCIONES DE IMPLEMENTACIÓN:")
        print("   1. Menú simple en el menú principal")
        print("   2. Submenú dedicado con todas las opciones")
        print("   3. Integrado en el menú de macros existente")
    else:
        print("\n✅ Ya existe alguna gestión de macros")