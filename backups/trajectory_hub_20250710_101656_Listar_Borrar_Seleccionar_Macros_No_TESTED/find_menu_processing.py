#!/usr/bin/env python3
"""
🔍 Busca cómo se procesan las opciones del menú
⚡ Para saber dónde añadir el caso para delete
"""

def find_menu_processing():
    """Encuentra cómo se procesan las opciones del menú"""
    
    print("🔍 BUSCANDO PROCESAMIENTO DE OPCIONES")
    print("=" * 60)
    
    controller_path = 'trajectory_hub/interface/interactive_controller.py'
    
    with open(controller_path, 'r') as f:
        lines = f.readlines()
    
    # Buscar process_choice o similar
    print("📋 BUSCANDO PROCESADORES:")
    
    # Buscar métodos que puedan procesar opciones
    process_methods = []
    for i, line in enumerate(lines):
        if 'def ' in line and ('process' in line.lower() or 'handle' in line.lower()):
            method_name = line.strip().split('(')[0].replace('def ', '')
            process_methods.append((i+1, method_name))
            print(f"   Línea {i+1}: {method_name}()")
    
    # Buscar específicamente process_choice
    print("\n📋 BUSCANDO process_choice:")
    process_choice_start = -1
    for i, line in enumerate(lines):
        if 'def process_choice' in line:
            process_choice_start = i
            print(f"✅ Encontrado en línea {i+1}")
            break
    
    if process_choice_start > 0:
        # Mostrar contenido
        print("\nCONTENIDO DE process_choice:")
        print("-" * 40)
        for i in range(process_choice_start, min(process_choice_start + 50, len(lines))):
            line = lines[i]
            print(f"{i+1:4d}: {line.rstrip()}")
            if i > process_choice_start and 'def ' in line and not line.startswith('        '):
                break
    
    # Buscar dónde se procesan las opciones del menú system
    print("\n📋 BUSCANDO PROCESAMIENTO DE OPCIONES 2 y 3:")
    for i, line in enumerate(lines):
        if ('choice == "2"' in line or 'choice == "3"' in line) and ('_list_active_macros' in lines[i+1] or '_show_macro_info' in lines[i+1]):
            print(f"\nEncontrado en línea {i+1}:")
            # Mostrar contexto
            for j in range(max(0, i-2), min(len(lines), i+5)):
                print(f"{j+1:4d}: {lines[j].rstrip()}")
    
    # Buscar el patrón específico del menú system
    print("\n📋 BUSCANDO PATRÓN elif EN current_menu == 'system':")
    in_system_section = False
    system_section_start = -1
    
    for i, line in enumerate(lines):
        if 'current_menu == "system"' in line:
            in_system_section = True
            system_section_start = i
            print(f"\n✅ Sección system encontrada en línea {i+1}")
            # Mostrar las siguientes líneas
            for j in range(i, min(i+30, len(lines))):
                if 'elif self.current_menu ==' in lines[j] and j > i:
                    print(f"\n[Fin de sección en línea {j}]")
                    break
                print(f"{j+1:4d}: {lines[j].rstrip()}")
            break
    
    return {
        'has_process_choice': process_choice_start > 0,
        'system_section_at': system_section_start
    }

if __name__ == "__main__":
    result = find_menu_processing()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    if result['has_process_choice']:
        print("   ✅ process_choice encontrado")
    if result['system_section_at'] > 0:
        print(f"   ✅ Sección system en línea {result['system_section_at'] + 1}")
        print("\n🎯 ACCIÓN: Añadir elif choice == '7' después de opción 6")