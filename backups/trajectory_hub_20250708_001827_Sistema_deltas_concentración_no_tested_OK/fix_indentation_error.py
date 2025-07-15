#!/usr/bin/env python3
"""
🔧 Fix: Corrige error de indentación en motion_components.py
⚡ Línea: 1142 - start_animation mal indentado
🎯 Solución: Arreglar indentación
"""

def fix_indentation():
    """Arregla la indentación en motion_components.py"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    print("🔧 Arreglando indentación...")
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    # Buscar la línea problemática
    for i in range(len(lines)):
        if i >= 1140 and i <= 1145:  # Alrededor de la línea 1142
            print(f"Línea {i+1}: {repr(lines[i][:50])}")
    
    # Arreglar la línea específica
    problem_line = 1141  # índice 1141 = línea 1142
    if problem_line < len(lines):
        # Ver la indentación de las líneas cercanas
        # Buscar la indentación correcta mirando métodos cercanos
        correct_indent = None
        
        # Buscar hacia atrás un def bien indentado
        for j in range(problem_line - 1, max(0, problem_line - 20), -1):
            if lines[j].strip().startswith('def ') and not lines[j].strip().startswith('def start_animation'):
                # Extraer la indentación
                indent = len(lines[j]) - len(lines[j].lstrip())
                correct_indent = ' ' * indent
                print(f"   Indentación detectada de línea {j+1}: {indent} espacios")
                break
        
        if correct_indent is None:
            # Usar 4 espacios por defecto para métodos de clase
            correct_indent = '    '
            print("   Usando indentación por defecto: 4 espacios")
        
        # Corregir la línea
        if 'def start_animation' in lines[problem_line]:
            lines[problem_line] = correct_indent + lines[problem_line].lstrip()
            print(f"   ✅ Línea {problem_line + 1} corregida")
    
    # Guardar
    with open(motion_file, 'w') as f:
        f.writelines(lines)
    
    print("✅ Indentación corregida")

def verify_fix():
    """Verifica que el archivo se puede importar"""
    print("\n🧪 Verificando...")
    try:
        import trajectory_hub.core.motion_components
        print("✅ motion_components.py importa correctamente")
        return True
    except IndentationError as e:
        print(f"❌ Todavía hay error de indentación: {e}")
        print(f"   Línea: {e.lineno}")
        
        # Mostrar contexto
        with open("trajectory_hub/core/motion_components.py", 'r') as f:
            lines = f.readlines()
            if e.lineno - 1 < len(lines):
                print(f"\nContexto (líneas {e.lineno-2} a {e.lineno+2}):")
                for i in range(max(0, e.lineno-3), min(len(lines), e.lineno+2)):
                    marker = ">>>" if i == e.lineno-1 else "   "
                    print(f"{marker} {i+1}: {repr(lines[i][:60])}")
        return False
    except Exception as e:
        print(f"✅ Otro tipo de error (indentación arreglada): {type(e).__name__}")
        return True

def smart_fix():
    """Fix más inteligente que busca el contexto completo"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar la clase ConcentrationComponent
    class_pos = content.find("class ConcentrationComponent")
    if class_pos == -1:
        print("❌ No se encuentra ConcentrationComponent")
        return
    
    # Buscar start_animation dentro de esa clase
    start_animation_pos = content.find("def start_animation", class_pos)
    if start_animation_pos == -1:
        print("❌ No se encuentra start_animation")
        return
    
    # Contar líneas hasta ese punto
    line_num = content[:start_animation_pos].count('\n') + 1
    print(f"   start_animation encontrado en línea {line_num}")
    
    # Verificar la indentación
    # Buscar la línea anterior que tenga un def
    lines_before = content[:start_animation_pos].split('\n')
    for i in range(len(lines_before) - 1, max(0, len(lines_before) - 50), -1):
        line = lines_before[i]
        if line.strip().startswith('def ') and 'def start_animation' not in line:
            indent = len(line) - len(line.lstrip())
            print(f"   Indentación correcta detectada: {indent} espacios")
            
            # Arreglar start_animation
            lines = content.split('\n')
            if line_num - 1 < len(lines):
                lines[line_num - 1] = ' ' * indent + lines[line_num - 1].lstrip()
                
                # Guardar
                with open(motion_file, 'w') as f:
                    f.write('\n'.join(lines))
                
                print("   ✅ Indentación corregida con smart fix")
                return
    
    print("   ❌ No se pudo determinar la indentación correcta")

if __name__ == "__main__":
    print("🔧 ARREGLANDO ERROR DE INDENTACIÓN\n")
    
    # Intentar fix normal
    fix_indentation()
    
    # Verificar
    if not verify_fix():
        print("\n🔄 Intentando smart fix...")
        smart_fix()
        verify_fix()
    
    print("\n✅ Ahora ejecuta:")
    print("$ python test_delta_final.py")