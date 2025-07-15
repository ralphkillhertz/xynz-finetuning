#!/usr/bin/env python3
"""
🔍 Muestra el contenido exacto del menú system
⚡ Para entender la estructura real
"""

def show_system_menu():
    """Muestra contenido exacto del menú system"""
    
    print("🔍 CONTENIDO EXACTO DEL MENÚ SYSTEM")
    print("=" * 60)
    
    controller_path = 'trajectory_hub/interface/interactive_controller.py'
    
    with open(controller_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar _show_system_menu
    menu_start = -1
    for i, line in enumerate(lines):
        if 'def _show_system_menu' in line:
            menu_start = i
            break
    
    if menu_start == -1:
        print("❌ No se encontró _show_system_menu")
        return
    
    print(f"📍 Encontrado en línea {menu_start + 1}\n")
    
    # Mostrar las siguientes 40 líneas
    print("CONTENIDO DEL MÉTODO:")
    print("-" * 60)
    
    # Determinar indentación del método
    method_indent = len(lines[menu_start]) - len(lines[menu_start].lstrip())
    
    for i in range(menu_start, min(menu_start + 40, len(lines))):
        line = lines[i]
        # Si llegamos a otro método al mismo nivel, parar
        if i > menu_start and line.strip().startswith('def ') and len(line) - len(line.lstrip()) <= method_indent:
            print(f"\n[Fin del método en línea {i}]")
            break
        
        # Mostrar línea con número
        print(f"{i+1:4d}: {line.rstrip()}")
    
    print("-" * 60)
    
    # Buscar patrones específicos
    print("\n📊 ANÁLISIS DE PATRONES:")
    
    # Volver a leer el método completo
    method_content = []
    for i in range(menu_start, len(lines)):
        line = lines[i]
        if i > menu_start and line.strip().startswith('def ') and len(line) - len(line.lstrip()) <= method_indent:
            break
        method_content.append(line)
    
    # Buscar diferentes patrones de menú
    patterns = {
        'options.append': 0,
        'print(': 0,
        'elif choice': 0,
        'if choice': 0,
        'ui.show_option': 0,
        'self.ui.': 0
    }
    
    for line in method_content:
        for pattern in patterns:
            if pattern in line:
                patterns[pattern] += 1
    
    print("Patrones encontrados:")
    for pattern, count in patterns.items():
        if count > 0:
            print(f"   {pattern}: {count} veces")
    
    # Buscar cómo se muestran las opciones
    print("\n📋 LÍNEAS CON OPCIONES/PRINTS:")
    for i, line in enumerate(method_content):
        if any(word in line for word in ['print(', 'show_option', '"1"', '"2"', '"3"', 'Listar', 'Info', 'choice']):
            print(f"   Línea {menu_start + i + 1}: {line.strip()}")

if __name__ == "__main__":
    show_system_menu()