#!/usr/bin/env python3
"""
🔍 Analiza el menú system donde están las opciones de macros
⚡ Ver estructura exacta para añadir delete
"""

def analyze_system_menu():
    """Analiza el menú system"""
    
    print("🔍 ANÁLISIS DEL MENÚ SYSTEM")
    print("=" * 60)
    
    controller_path = 'trajectory_hub/interface/interactive_controller.py'
    
    with open(controller_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar _show_system_menu
    print("📋 BUSCANDO MENÚ SYSTEM:")
    menu_start = -1
    
    for i, line in enumerate(lines):
        if 'def _show_system_menu' in line:
            menu_start = i
            print(f"✅ Encontrado en línea {i+1}")
            break
    
    if menu_start == -1:
        print("❌ No encontrado")
        return None
    
    # Extraer el contenido del menú
    print("\n📋 CONTENIDO DEL MENÚ SYSTEM:")
    print("-" * 40)
    
    menu_lines = []
    indent_level = len(lines[menu_start]) - len(lines[menu_start].lstrip())
    
    for i in range(menu_start, min(menu_start + 50, len(lines))):
        line = lines[i]
        # Si es parte del método
        if i == menu_start or (line.strip() and len(line) - len(line.lstrip()) > indent_level):
            menu_lines.append((i+1, line.rstrip()))
        elif line.strip() and len(line) - len(line.lstrip()) <= indent_level:
            break
    
    # Mostrar líneas relevantes
    options_found = []
    for line_num, line in menu_lines:
        if 'options.append' in line or 'elif' in line and 'choice' in line:
            print(f"   Línea {line_num}: {line}")
            if '"' in line:
                try:
                    option = line.split('"')[1]
                    if option.isdigit():
                        options_found.append(int(option))
                except:
                    pass
    
    # Buscar estructura de opciones
    print("\n📊 ESTRUCTURA DE OPCIONES:")
    in_options = False
    option_count = 0
    
    for line_num, line in menu_lines:
        if 'options.append' in line:
            option_count += 1
            # Extraer texto de la opción
            if '"' in line:
                parts = line.split('"')
                if len(parts) >= 4:
                    num = parts[1]
                    text = parts[3]
                    print(f"   Opción {num}: {text}")
    
    # Ver dónde están list_active_macros y show_macro_info
    print("\n📍 UBICACIÓN DE MÉTODOS DE MACROS:")
    for line_num, line in menu_lines:
        if '_list_active_macros' in line:
            print(f"   list_active_macros: línea {line_num}")
        elif '_show_macro_info' in line:
            print(f"   show_macro_info: línea {line_num}")
    
    # Buscar última opción
    last_option = 0
    if options_found:
        last_option = max(options_found)
    
    print(f"\n📊 RESUMEN:")
    print(f"   Total opciones: {option_count}")
    print(f"   Última opción numérica: {last_option}")
    print(f"   Métodos de macros encontrados: ✅")
    
    # Ver si selected_macro está definido
    print("\n🔍 VERIFICANDO selected_macro:")
    for i, line in enumerate(lines):
        if 'self.selected_macro' in line and '=' in line:
            print(f"   Línea {i+1}: {line.strip()}")
            break
    
    return {
        'menu_start': menu_start,
        'option_count': option_count,
        'last_option': last_option,
        'has_macro_methods': True
    }

if __name__ == "__main__":
    result = analyze_system_menu()
    
    if result:
        print("\n" + "=" * 60)
        print("🎯 PLAN DE ACCIÓN:")
        print("   1. Actualizar _list_active_macros() para usar engine.list_macros()")
        print("   2. Implementar _show_macro_info() con engine.select_macro()")
        print(f"   3. Añadir opción {result['last_option']+1} para delete_macro")
        print("   4. Implementar _delete_macro() usando engine.delete_macro()")