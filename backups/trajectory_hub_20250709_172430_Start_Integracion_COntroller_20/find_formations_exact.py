def find_formations_exact():
    print("🔍 BÚSQUEDA EXACTA DE FORMACIONES")
    print("="*60)
    
    controller_file = "trajectory_hub/interface/interactive_controller.py"
    
    with open(controller_file, 'r') as f:
        content = f.read()
    
    # Buscar patrones exactos que vemos en el menú
    patterns = [
        "1. circle",
        "2. line", 
        "3. grid",
        "4. spiral",
        "5. random",
        "print.*circle.*line.*grid",
        'circle.*line.*grid.*spiral.*random'
    ]
    
    import re
    
    for pattern in patterns:
        matches = list(re.finditer(pattern, content, re.IGNORECASE | re.DOTALL))
        if matches:
            print(f"\n✅ Patrón encontrado: '{pattern[:30]}...'")
            for match in matches[:3]:  # Primeros 3
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end].replace('\n', '\\n')
                print(f"   Contexto: ...{context}...")
                
                # Obtener número de línea
                line_num = content[:match.start()].count('\n') + 1
                print(f"   Línea ~{line_num}")
    
    # Buscar handle_create_macro específicamente
    print("\n🔍 Buscando handle_create_macro...")
    handle_match = re.search(r'def handle_create_macro.*?(?=\n    def|\n\nclass|\Z)', content, re.DOTALL)
    
    if handle_match:
        method_content = handle_match.group(0)
        print(f"✅ Encontrado handle_create_macro ({len(method_content)} caracteres)")
        
        # Buscar el print con las formaciones
        formation_print = re.search(r'print\([^)]*\).*?print\([^)]*\).*?print\([^)]*random[^)]*\)', method_content, re.DOTALL)
        
        if formation_print:
            print("\n📋 Bloque de formaciones encontrado:")
            print(formation_print.group(0)[:200] + "...")
            
            # Extraer y modificar
            old_block = formation_print.group(0)
            if "6. sphere" not in old_block:
                # Añadir sphere
                new_block = old_block.replace("5. random", "5. random\\n  6. sphere")
                method_content = method_content.replace(old_block, new_block)
                
                # También buscar el diccionario
                dict_match = re.search(r'(formation(?:s|_map)?\s*=\s*\{[^}]+\})', method_content)
                if dict_match:
                    old_dict = dict_match.group(1)
                    if '"6": "sphere"' not in old_dict:
                        new_dict = old_dict.rstrip('}') + ', "6": "sphere"}'
                        method_content = method_content.replace(old_dict, new_dict)
                
                # Reemplazar en el contenido completo
                new_content = content.replace(handle_match.group(0), method_content)
                
                # Guardar
                import shutil
                from datetime import datetime
                backup = f"{controller_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy(controller_file, backup)
                
                with open(controller_file, 'w') as f:
                    f.write(new_content)
                
                print("\n✅ Formación SPHERE añadida")
                return True
    
    # Si no encontramos, buscar de otra manera
    print("\n🔍 Búsqueda alternativa...")
    
    # Buscar línea por línea
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "1. circle" in line:
            print(f"\n✅ Encontrado en línea {i+1}: {line}")
            
            # Mostrar contexto
            for j in range(max(0, i-2), min(len(lines), i+8)):
                print(f"   {j+1}: {lines[j]}")
            
            # Insertar sphere si no está
            if i+4 < len(lines) and "5. random" in lines[i+4] and "6. sphere" not in lines[i+5]:
                lines.insert(i+5, "  6. sphere")
                print("\n✅ Insertando sphere después de random")
                
                # Guardar
                with open(controller_file, 'w') as f:
                    f.write('\n'.join(lines))
                
                return True
    
    print("\n❌ No pude encontrar el menú de formaciones")
    return False

if __name__ == "__main__":
    if find_formations_exact():
        print("\n🚀 Prueba ahora: python main.py --interactive")