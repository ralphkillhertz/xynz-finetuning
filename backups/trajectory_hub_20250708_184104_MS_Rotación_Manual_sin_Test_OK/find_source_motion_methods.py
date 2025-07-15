# find_source_motion_methods.py
# Busca todos los métodos en SourceMotion

def find_source_motion():
    print("🔍 Buscando la clase SourceMotion y sus métodos...")
    
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Buscar la clase SourceMotion
    in_source_motion = False
    source_motion_start = -1
    class_indent = 0
    methods_found = []
    
    for i, line in enumerate(lines):
        if 'class SourceMotion' in line:
            in_source_motion = True
            source_motion_start = i
            class_indent = len(line) - len(line.lstrip())
            print(f"✅ Encontrada clase SourceMotion en línea {i + 1}")
            print(f"   Indentación de la clase: {class_indent} espacios")
            continue
            
        if in_source_motion:
            # Si encontramos otra clase al mismo nivel, terminamos
            if line.strip().startswith('class ') and (len(line) - len(line.lstrip()) == class_indent):
                break
                
            # Buscar métodos
            if line.strip().startswith('def '):
                method_name = line.strip().split('(')[0].replace('def ', '')
                methods_found.append((i + 1, method_name, line.strip()))
    
    print(f"\n📋 Métodos encontrados en SourceMotion:")
    for line_num, method_name, full_line in methods_found:
        print(f"   Línea {line_num}: {method_name}")
        if 'update' in method_name.lower():
            print(f"      >>> {full_line}")
    
    # Buscar específicamente métodos que contengan "update"
    print("\n🔍 Buscando métodos con 'update' en el nombre:")
    update_methods = [(ln, mn, fl) for ln, mn, fl in methods_found if 'update' in mn.lower()]
    
    if update_methods:
        for line_num, method_name, full_line in update_methods:
            print(f"\n📌 Método: {method_name} (línea {line_num})")
            # Mostrar las primeras líneas del método
            method_indent = len(lines[line_num - 1]) - len(lines[line_num - 1].lstrip())
            print("   Contenido:")
            for j in range(line_num - 1, min(line_num + 10, len(lines))):
                if j > line_num and lines[j].strip() and (len(lines[j]) - len(lines[j].lstrip()) <= method_indent):
                    break
                print(f"   {j+1:4d}: {lines[j]}")
    else:
        print("   ❌ No se encontraron métodos con 'update'")
    
    # Buscar en engine qué método llama
    print("\n🔍 Verificando qué llama engine.update()...")
    
    with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
        engine_content = f.read()
    
    engine_lines = engine_content.split('\n')
    for i, line in enumerate(engine_lines):
        if 'motion.' in line and 'update' in line and 'self.motion_states' in engine_lines[max(0, i-5):i+5]:
            print(f"   Línea {i+1}: {line.strip()}")

if __name__ == "__main__":
    find_source_motion()
    
    print("\n💡 Basado en lo encontrado, crearemos el método correcto.")