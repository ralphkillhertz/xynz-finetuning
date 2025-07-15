#!/usr/bin/env python3
"""
🔍 Diagnóstico completo del Interactive Controller
⚡ Analiza estructura, menús y métodos existentes
"""

def diagnose_controller():
    """Diagnóstico completo del controller"""
    
    print("🔍 DIAGNÓSTICO DE INTERACTIVE CONTROLLER")
    print("=" * 60)
    
    controller_path = 'trajectory_hub/interface/interactive_controller.py'
    
    with open(controller_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')
    
    # 1. Analizar menú principal
    print("\n📋 MENÚ PRINCIPAL:")
    in_main_menu = False
    menu_options = {}
    menu_section_start = -1
    
    for i, line in enumerate(lines):
        if 'def show_main_menu' in line:
            in_main_menu = True
            menu_section_start = i
        elif in_main_menu and 'options = {' in line:
            # Comenzar a capturar opciones
            j = i + 1
            while j < len(lines) and '}' not in lines[j]:
                if '"' in lines[j] and '":' in lines[j]:
                    parts = lines[j].split('"')
                    if len(parts) >= 4:
                        num = parts[1]
                        desc = parts[3]
                        menu_options[num] = desc
                        print(f"   {num}. {desc}")
                j += 1
            in_main_menu = False
    
    # 2. Buscar métodos relacionados con macros
    print("\n🔍 MÉTODOS RELACIONADOS CON MACROS:")
    macro_methods = []
    show_methods = []
    
    for i, line in enumerate(lines):
        if 'def ' in line:
            if 'macro' in line.lower():
                method_name = line.strip().split('(')[0].replace('def ', '')
                macro_methods.append((i+1, method_name))
            elif 'show_' in line:
                method_name = line.strip().split('(')[0].replace('def ', '')
                show_methods.append((i+1, method_name))
    
    if macro_methods:
        for line_num, method in macro_methods[:10]:
            print(f"   Línea {line_num}: {method}()")
    else:
        print("   ❌ No hay métodos con 'macro' en el nombre")
    
    # 3. Analizar estructura de cases en el menú
    print("\n🔍 ESTRUCTURA DE CASES:")
    case_structure = []
    
    for i, line in enumerate(lines):
        if 'elif choice ==' in line and '"' in line:
            choice_num = line.split('"')[1]
            # Ver qué hace
            next_line = lines[i+1].strip() if i+1 < len(lines) else ""
            case_structure.append((choice_num, next_line))
    
    for choice, action in case_structure:
        print(f"   Opción {choice}: {action}")
    
    # 4. Buscar si ya hay algún tipo de gestión
    print("\n🔍 GESTIÓN EXISTENTE:")
    keywords = ['list_macro', 'delete_macro', 'select_macro', 'manage_macro']
    found_management = []
    
    for keyword in keywords:
        if keyword in content:
            found_management.append(keyword)
    
    if found_management:
        print(f"   ✅ Encontrado: {', '.join(found_management)}")
    else:
        print("   ❌ No se encontró gestión de macros")
    
    # 5. Analizar métodos show_*
    print("\n📋 MÉTODOS DE VISUALIZACIÓN (show_*):")
    for line_num, method in show_methods[:10]:
        print(f"   Línea {line_num}: {method}()")
    
    # 6. Buscar última línea de la clase
    class_end = -1
    for i in range(len(lines)-1, 0, -1):
        if 'if __name__ == "__main__"' in lines[i]:
            class_end = i
            break
    
    print(f"\n📍 INFORMACIÓN ESTRUCTURAL:")
    print(f"   Total líneas: {len(lines)}")
    print(f"   Menú principal en línea: {menu_section_start + 1}")
    print(f"   Última opción del menú: {max(menu_options.keys()) if menu_options else 0}")
    print(f"   Final de la clase: línea {class_end}")
    
    # 7. Verificar si el engine está accesible
    has_engine = 'self.engine' in content
    has_list_macros = 'self.engine.list_macros' in content
    
    print(f"\n🔧 INTEGRACIÓN CON ENGINE:")
    print(f"   self.engine disponible: {'✅' if has_engine else '❌'}")
    print(f"   Usa list_macros(): {'✅' if has_list_macros else '❌'}")
    
    return {
        'menu_options': menu_options,
        'last_option': max(menu_options.keys()) if menu_options else "0",
        'has_macro_management': len(found_management) > 0,
        'show_methods_count': len(show_methods),
        'class_ends_at': class_end,
        'menu_starts_at': menu_section_start
    }

if __name__ == "__main__":
    result = diagnose_controller()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO:")
    print(f"   Opciones en menú: {len(result['menu_options'])}")
    print(f"   Última opción: {result['last_option']}")
    print(f"   Gestión de macros: {'✅ SÍ' if result['has_macro_management'] else '❌ NO'}")
    print(f"   Métodos show_*: {result['show_methods_count']}")
    
    if not result['has_macro_management']:
        print(f"\n🎯 RECOMENDACIÓN:")
        print(f"   Añadir opción '{int(result['last_option'])+1}' al menú")
        print(f"   Insertar método show_macro_management()")
        print(f"   Ubicación: antes de línea {result['class_ends_at']}")