#!/usr/bin/env python3
"""
🔧 Fix: Arregla TODOS los errores de indentación en ConcentrationComponent
⚡ Problema: Múltiples métodos mal indentados
🎯 Solución: Re-indentar toda la clase correctamente
"""

import re

def fix_concentration_component():
    """Arregla toda la clase ConcentrationComponent"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    print("🔧 Arreglando TODA la clase ConcentrationComponent...")
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar la clase ConcentrationComponent
    class_match = re.search(r'(class ConcentrationComponent.*?)((?=\nclass )|(?=\n@dataclass)|$)', 
                           content, re.DOTALL)
    
    if not class_match:
        print("❌ No se encuentra ConcentrationComponent")
        return
    
    class_content = class_match.group(1)
    rest_of_file = content[class_match.end():]
    before_class = content[:class_match.start()]
    
    print(f"   Clase encontrada, {len(class_content.split(chr(10)))} líneas")
    
    # Separar en líneas
    lines = class_content.split('\n')
    fixed_lines = []
    
    # La primera línea (class ...) debe tener indentación 0
    class_indent = 0
    method_indent = 4  # Los métodos deben tener 4 espacios
    body_indent = 8    # El cuerpo de los métodos debe tener 8 espacios
    
    inside_method = False
    inside_docstring = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Línea vacía - mantener
        if not stripped:
            fixed_lines.append('')
            continue
        
        # Definición de clase
        if stripped.startswith('class ConcentrationComponent'):
            fixed_lines.append(stripped)
            continue
        
        # Docstring de clase
        if i == 1 and stripped.startswith('"""'):
            fixed_lines.append(' ' * method_indent + stripped)
            continue
        
        # Método __init__
        if stripped.startswith('def __init__'):
            fixed_lines.append(' ' * method_indent + stripped)
            inside_method = True
            continue
        
        # Otros métodos
        if stripped.startswith('def '):
            fixed_lines.append(' ' * method_indent + stripped)
            inside_method = True
            continue
        
        # Decorador de propiedad
        if stripped.startswith('@property'):
            fixed_lines.append(' ' * method_indent + stripped)
            continue
        
        # Contenido de métodos
        if inside_method:
            # Docstring
            if stripped.startswith('"""'):
                fixed_lines.append(' ' * body_indent + stripped)
                if stripped.endswith('"""') and len(stripped) > 6:
                    # Docstring de una línea
                    pass
                else:
                    inside_docstring = not inside_docstring
            else:
                # Código normal
                fixed_lines.append(' ' * body_indent + stripped)
        else:
            # Atributos de clase u otro contenido
            fixed_lines.append(' ' * method_indent + stripped)
    
    # Reconstruir la clase
    fixed_class = '\n'.join(fixed_lines)
    
    # Reconstruir el archivo completo
    new_content = before_class + fixed_class + '\n' + rest_of_file
    
    # Guardar
    with open(motion_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Clase ConcentrationComponent re-indentada completamente")

def fix_calculate_delta():
    """Asegura que calculate_delta esté bien posicionado"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Verificar si calculate_delta existe y está bien ubicado
    if "def calculate_delta" in content:
        # Buscar su posición
        calc_pos = content.find("def calculate_delta")
        
        # Contar líneas hasta ahí
        line_num = content[:calc_pos].count('\n') + 1
        
        # Ver si está dentro de ConcentrationComponent
        before_calc = content[:calc_pos]
        last_class = before_calc.rfind("class ")
        
        if last_class != -1:
            class_line = before_calc[last_class:].split('\n')[0]
            if "ConcentrationComponent" in class_line:
                print("✅ calculate_delta está en ConcentrationComponent")
            else:
                print("⚠️ calculate_delta NO está en ConcentrationComponent")
                # Moverlo
                move_calculate_delta()

def move_calculate_delta():
    """Mueve calculate_delta dentro de ConcentrationComponent"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar calculate_delta
    calc_start = -1
    calc_end = -1
    
    for i, line in enumerate(lines):
        if 'def calculate_delta' in line and calc_start == -1:
            calc_start = i
            # Buscar el final del método
            indent = len(line) - len(line.lstrip())
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith(' ' * (indent + 1)):
                    calc_end = j
                    break
    
    if calc_start == -1:
        print("   ❌ No se encuentra calculate_delta")
        return
    
    # Extraer el método
    calc_method = lines[calc_start:calc_end]
    
    # Eliminar del lugar actual
    del lines[calc_start:calc_end]
    
    # Buscar dónde insertarlo en ConcentrationComponent
    for i, line in enumerate(lines):
        if 'class ConcentrationComponent' in line:
            # Buscar el método update
            for j in range(i, len(lines)):
                if '    def update(' in lines[j]:
                    # Insertar antes de update
                    lines[j:j] = calc_method
                    print("   ✅ calculate_delta movido a ConcentrationComponent")
                    break
            break
    
    # Guardar
    with open(motion_file, 'w') as f:
        f.writelines(lines)

def verify_all():
    """Verifica que todo funciona"""
    print("\n🧪 Verificando importación...")
    try:
        import trajectory_hub.core.motion_components as mc
        print("✅ motion_components importa correctamente")
        
        # Verificar que ConcentrationComponent tiene calculate_delta
        if hasattr(mc.ConcentrationComponent, 'calculate_delta'):
            print("✅ ConcentrationComponent tiene calculate_delta")
        else:
            print("❌ ConcentrationComponent NO tiene calculate_delta")
            
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 ARREGLANDO TODOS LOS ERRORES DE INDENTACIÓN\n")
    
    # 1. Arreglar toda la clase
    fix_concentration_component()
    
    # 2. Verificar calculate_delta
    fix_calculate_delta()
    
    # 3. Verificar
    if verify_all():
        print("\n✅ TODO ARREGLADO! Ejecuta:")
        print("$ python test_delta_final.py")
    else:
        print("\n❌ Aún hay problemas")