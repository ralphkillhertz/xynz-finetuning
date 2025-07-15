#!/usr/bin/env python3
"""
🔧 Fix: Arregla error específico en línea 1075
⚡ Error: expected an indented block
🎯 Solución: Encontrar y arreglar el bloque vacío
"""

def fix_specific_line():
    """Arregla el error en línea 1075"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    print("🔍 Buscando error en línea 1075...")
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    # Mostrar contexto alrededor de línea 1075
    target_line = 1074  # índice 1074 = línea 1075
    
    print(f"\nContexto (líneas 1070-1080):")
    for i in range(max(0, target_line - 5), min(len(lines), target_line + 5)):
        marker = ">>>" if i == target_line else "   "
        print(f"{marker} {i+1}: {repr(lines[i][:60])}")
    
    # Buscar el problema
    if target_line < len(lines):
        current_line = lines[target_line].rstrip()
        prev_line = lines[target_line - 1].rstrip() if target_line > 0 else ""
        
        # Si la línea anterior termina con : y la actual está vacía
        if prev_line.endswith(':') and not current_line.strip():
            print("\n❌ Encontrado: bloque vacío después de :")
            
            # Añadir 'pass' con la indentación correcta
            indent = len(prev_line) - len(prev_line.lstrip()) + 4
            lines[target_line] = ' ' * indent + 'pass\n'
            print(f"✅ Añadido 'pass' con {indent} espacios de indentación")
            
            # Guardar
            with open(motion_file, 'w') as f:
                f.writelines(lines)
            
            return True
    
    return False

def find_all_empty_blocks():
    """Encuentra y arregla TODOS los bloques vacíos"""
    motion_file = "trajectory_hub/core/motion_components.py"
    
    print("\n🔍 Buscando TODOS los bloques vacíos...")
    
    with open(motion_file, 'r') as f:
        lines = f.readlines()
    
    fixed_count = 0
    i = 0
    
    while i < len(lines) - 1:
        line = lines[i].rstrip()
        
        # Si la línea termina con :
        if line.endswith(':'):
            # Ver la siguiente línea
            next_line_idx = i + 1
            
            # Saltar líneas vacías
            while next_line_idx < len(lines) and not lines[next_line_idx].strip():
                next_line_idx += 1
            
            # Si la siguiente línea no vacía no tiene más indentación, hay un problema
            if next_line_idx < len(lines):
                next_line = lines[next_line_idx]
                current_indent = len(line) - len(line.lstrip())
                next_indent = len(next_line) - len(next_line.lstrip())
                
                if next_line.strip() and next_indent <= current_indent:
                    # Necesitamos añadir pass
                    print(f"   Línea {i+1}: Bloque vacío encontrado")
                    indent = current_indent + 4
                    lines.insert(i + 1, ' ' * indent + 'pass\n')
                    fixed_count += 1
                    i += 1  # Saltar la línea que acabamos de insertar
        
        i += 1
    
    if fixed_count > 0:
        # Guardar
        with open(motion_file, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ {fixed_count} bloques vacíos arreglados")
    else:
        print("✅ No se encontraron bloques vacíos")
    
    return fixed_count

def check_syntax():
    """Verifica la sintaxis del archivo"""
    print("\n🧪 Verificando sintaxis...")
    
    import ast
    motion_file = "trajectory_hub/core/motion_components.py"
    
    try:
        with open(motion_file, 'r') as f:
            content = f.read()
        
        ast.parse(content)
        print("✅ Sintaxis correcta!")
        return True
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en línea {e.lineno}: {e.msg}")
        
        # Mostrar contexto
        with open(motion_file, 'r') as f:
            lines = f.readlines()
        
        if e.lineno and e.lineno <= len(lines):
            print(f"\nContexto:")
            for i in range(max(0, e.lineno - 3), min(len(lines), e.lineno + 2)):
                marker = ">>>" if i == e.lineno - 1 else "   "
                print(f"{marker} {i+1}: {lines[i].rstrip()}")
        
        return False

if __name__ == "__main__":
    print("🔧 ARREGLANDO ERROR EN LÍNEA 1075\n")
    
    # Primero intentar arreglar la línea específica
    if not fix_specific_line():
        # Si no funciona, buscar todos los bloques vacíos
        find_all_empty_blocks()
    
    # Verificar sintaxis
    if check_syntax():
        print("\n✅ TODO ARREGLADO! Ejecuta:")
        print("$ python test_delta_final.py")
    else:
        print("\n⚠️ Puede que necesites ejecutar el script otra vez")