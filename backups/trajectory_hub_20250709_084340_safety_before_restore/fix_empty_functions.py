# === fix_empty_functions.py ===
# 🔧 Fix: Añadir cuerpo a funciones vacías
# ⚡ Después de mover docstrings, algunas funciones quedaron sin código

import os

def fix_empty_functions():
    """Arreglar funciones que quedaron sin cuerpo"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_empty', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Buscando funciones sin cuerpo...")
    
    # Mostrar contexto del error
    print("\n📋 Contexto alrededor de línea 110:")
    for i in range(max(0, 105), min(115, len(lines))):
        if i < len(lines):
            marker = ">>>" if i == 109 else "   "
            print(f"{marker} {i+1}: {lines[i].rstrip()}")
    
    # Buscar funciones que terminan con : y no tienen código después
    i = 0
    fixes = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Si es una definición de función que termina con :
        if ('def ' in line or line.strip().endswith(':')) and ':' in line:
            # Verificar si la siguiente línea está vacía o no está indentada
            if i+1 < len(lines):
                next_line = lines[i+1]
                
                # Si la siguiente línea no está indentada (debe estarlo)
                if next_line.strip() and not next_line.startswith(' ') and not next_line.startswith('\t'):
                    print(f"\n❌ Función sin cuerpo en línea {i+1}")
                    print(f"   {line.strip()}")
                    
                    # Obtener la indentación correcta
                    base_indent = len(line) - len(line.lstrip())
                    body_indent = ' ' * (base_indent + 4)
                    
                    # Insertar pass
                    lines.insert(i+1, f"{body_indent}pass\n")
                    print(f"✅ Añadido 'pass' temporal")
                    fixes += 1
                    i += 1  # Saltar la línea insertada
                    
                # Si la siguiente línea está vacía, verificar si hay algo más
                elif not next_line.strip():
                    # Buscar la primera línea no vacía
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    
                    if j < len(lines):
                        # Verificar la indentación de esa línea
                        check_line = lines[j]
                        if check_line.strip() and not check_line.startswith(' ') and not check_line.startswith('\t'):
                            # No hay código indentado
                            print(f"\n❌ Función sin cuerpo en línea {i+1}")
                            
                            base_indent = len(line) - len(line.lstrip())
                            body_indent = ' ' * (base_indent + 4)
                            
                            # Insertar pass después de los espacios en blanco
                            lines.insert(i+1, f"{body_indent}pass\n")
                            print(f"✅ Añadido 'pass' temporal")
                            fixes += 1
        
        i += 1
    
    # Fix específico para __init__ si es necesario
    print("\n🔧 Verificando __init__ específicamente...")
    
    for i in range(len(lines)):
        if 'def __init__' in lines[i]:
            print(f"📍 __init__ encontrado en línea {i+1}")
            
            # Buscar el final de la definición
            j = i
            while j < len(lines) and not lines[j].rstrip().endswith(':'):
                j += 1
            
            if j < len(lines):
                # Verificar si hay docstring
                k = j + 1
                has_docstring = False
                docstring_end = k
                
                # Saltar líneas vacías
                while k < len(lines) and not lines[k].strip():
                    k += 1
                
                if k < len(lines) and lines[k].strip().startswith('"""'):
                    has_docstring = True
                    # Buscar el final de la docstring
                    while k < len(lines) and not (k > j+1 and '"""' in lines[k]):
                        k += 1
                    docstring_end = k
                
                # Verificar si hay código después de la docstring
                next_code = docstring_end + 1
                while next_code < len(lines) and not lines[next_code].strip():
                    next_code += 1
                
                if next_code < len(lines):
                    next_line = lines[next_code]
                    base_indent = len(lines[i]) - len(lines[i].lstrip())
                    expected_indent = base_indent + 4
                    actual_indent = len(next_line) - len(next_line.lstrip())
                    
                    if actual_indent < expected_indent and next_line.strip():
                        print(f"❌ Código mal indentado después de __init__")
                        # Debe haber código que pertenece a __init__ pero no está indentado
                        # Buscar hasta dónde debería llegar __init__
                        end_of_init = next_code
                        while end_of_init < len(lines):
                            if ('def ' in lines[end_of_init] or 
                                'class ' in lines[end_of_init] or
                                (lines[end_of_init].strip() and 
                                 len(lines[end_of_init]) - len(lines[end_of_init].lstrip()) <= base_indent)):
                                break
                            end_of_init += 1
                        
                        # Indentar todo el código
                        for m in range(next_code, end_of_init):
                            if lines[m].strip():
                                current_indent = len(lines[m]) - len(lines[m].lstrip())
                                lines[m] = ' ' * expected_indent + lines[m].lstrip()
                        
                        print(f"✅ Indentado código de __init__ ({end_of_init - next_code} líneas)")
                        fixes += 1
            break
    
    print(f"\n✅ Total de {fixes} correcciones aplicadas")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def final_test():
    """Test final del sistema"""
    print("\n🧪 Test final...")
    
    import subprocess
    
    # Test de sintaxis
    result = subprocess.run(
        ['python', '-m', 'py_compile', 'trajectory_hub/core/enhanced_trajectory_engine.py'],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print("✅ ¡SINTAXIS CORRECTA!")
        
        # Ejecutar test del sistema
        print("\n🚀 Ejecutando test_delta_100.py...")
        print("⏳ Esto puede tardar un momento...")
        
        result = subprocess.run(['python', 'test_delta_100.py'], 
                              capture_output=True, text=True, timeout=60)
        
        # Analizar resultados
        if result.stdout:
            # Buscar el resumen final
            lines = result.stdout.split('\n')
            
            # Mostrar errores si hay
            errors_shown = False
            for line in lines:
                if 'Error' in line and 'Error:' in line:
                    if not errors_shown:
                        print("\n⚠️ Errores encontrados:")
                        errors_shown = True
                    print(f"   {line.strip()}")
            
            # Mostrar resumen
            print("\n📊 RESUMEN:")
            for line in lines[-30:]:
                if any(word in line for word in ['%', 'funcional', 'RESUMEN', 'Concentración']):
                    print(line)
            
            # Verificar estado final
            if '100%' in result.stdout:
                print("\n" + "="*60)
                print("🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL! 🎉")
                print("="*60)
            elif '25%' in result.stdout:
                print("\n⚠️ Sistema parcialmente funcional (25%)")
                print("💡 Revisar errores arriba para completar")
                
    else:
        print(f"❌ Error de sintaxis:\n{result.stderr}")
        # Mostrar línea específica
        import re
        match = re.search(r'line (\d+)', result.stderr)
        if match:
            line_num = int(match.group(1))
            print(f"\n📍 Error en línea {line_num}")

if __name__ == "__main__":
    print("🔧 FIXING EMPTY FUNCTIONS")
    print("=" * 60)
    
    fix_empty_functions()
    final_test()