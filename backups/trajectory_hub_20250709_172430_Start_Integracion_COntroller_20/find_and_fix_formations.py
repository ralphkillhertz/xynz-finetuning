def find_and_fix_formations():
    print("🔍 BÚSQUEDA PROFUNDA DE FORMACIONES")
    print("="*60)
    
    controller_file = "trajectory_hub/interface/interactive_controller.py"
    
    with open(controller_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar todas las líneas que contengan "circle", "spiral", "random"
    formation_lines = []
    for i, line in enumerate(lines):
        if any(form in line.lower() for form in ["circle", "spiral", "random", "formación"]):
            formation_lines.append((i+1, line.strip()))
    
    print("📋 Líneas con formaciones encontradas:")
    for line_num, line_text in formation_lines[:10]:  # Mostrar primeras 10
        print(f"   Línea {line_num}: {line_text[:60]}...")
    
    # Buscar específicamente el bloque del menú
    in_formation_menu = False
    menu_start = -1
    menu_end = -1
    
    for i, line in enumerate(lines):
        if "Formación inicial:" in line:
            in_formation_menu = True
            menu_start = i
            print(f"\n✅ Menú de formaciones encontrado en línea {i+1}")
            continue
            
        if in_formation_menu and "Opción:" in line:
            menu_end = i
            in_formation_menu = False
            break
    
    if menu_start >= 0 and menu_end >= 0:
        print(f"📍 Menú: líneas {menu_start+1} a {menu_end+1}")
        
        # Mostrar el menú actual
        print("\n📋 Menú actual:")
        for i in range(menu_start, menu_end+1):
            print(f"   {lines[i]}", end='')
        
        # Verificar si sphere está
        menu_text = ''.join(lines[menu_start:menu_end+1])
        if "sphere" not in menu_text:
            print("\n❌ 'sphere' NO está en el menú")
            
            # Insertar sphere
            for i in range(menu_start, menu_end):
                if "5. random" in lines[i]:
                    # Insertar después de random
                    lines.insert(i+1, "  6. sphere\n")
                    print("✅ Insertando '6. sphere' después de random")
                    break
        
        # Ahora buscar el diccionario de formaciones
        formations_dict_start = -1
        for i in range(menu_end, min(menu_end+50, len(lines))):
            if "formations = {" in lines[i] or "formations_map = {" in lines[i]:
                formations_dict_start = i
                print(f"\n✅ Diccionario de formaciones en línea {i+1}")
                break
        
        if formations_dict_start >= 0:
            # Buscar el cierre del diccionario
            brace_count = 0
            dict_end = -1
            for i in range(formations_dict_start, len(lines)):
                brace_count += lines[i].count('{') - lines[i].count('}')
                if brace_count == 0 and i > formations_dict_start:
                    dict_end = i
                    break
            
            if dict_end > 0:
                # Verificar si sphere está en el dict
                dict_text = ''.join(lines[formations_dict_start:dict_end+1])
                if '"6": "sphere"' not in dict_text:
                    # Insertar antes del cierre
                    for i in range(dict_end, formations_dict_start, -1):
                        if "}" in lines[i] and '"5"' in lines[i-1]:
                            lines[i] = lines[i].replace("}", ',\n            "6": "sphere"\n        }')
                            print("✅ Añadido '6': 'sphere' al diccionario")
                            break
        
        # Guardar cambios
        import shutil
        from datetime import datetime
        backup = f"{controller_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(controller_file, backup)
        print(f"\n💾 Backup: {backup}")
        
        with open(controller_file, 'w') as f:
            f.writelines(lines)
        
        print("✅ Archivo actualizado")
    
    else:
        print("❌ No encontré el menú de formaciones")
    
    # Test inmediato
    print("\n🧪 Test inmediato:")
    test = '''from trajectory_hub.interface.interactive_controller import InteractiveController
from trajectory_hub import EnhancedTrajectoryEngine

# Verificar que el menú tiene sphere
with open("trajectory_hub/interface/interactive_controller.py", "r") as f:
    content = f.read()
    if "6. sphere" in content:
        print("✅ '6. sphere' está en el archivo")
    else:
        print("❌ '6. sphere' NO está en el archivo")
        
    # Contar cuántas veces aparece sphere
    count = content.count("sphere")
    print(f"📊 'sphere' aparece {count} veces en el archivo")
'''
    
    with open("verify_sphere.py", "w") as f:
        f.write(test)
    
    print("🚀 Ejecuta: python verify_sphere.py")

if __name__ == "__main__":
    find_and_fix_formations()