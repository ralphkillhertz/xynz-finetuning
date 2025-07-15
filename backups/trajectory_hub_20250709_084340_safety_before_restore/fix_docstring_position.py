# === fix_docstring_position.py ===
# 🔧 Fix: Mover docstring al lugar correcto
# ⚡ Línea 263 tiene docstring pero hay código antes

import os

def fix_docstring_position():
    """Arreglar posición de docstrings mal ubicadas"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_docstring', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Buscando docstrings mal ubicadas...")
    
    # Buscar patrones de docstring después de código
    i = 0
    fixes = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Si encontramos una docstring (""")
        if line.startswith('"""') and i > 0:
            # Verificar si hay código antes (no solo la definición de función)
            # Buscar hacia atrás la definición de función más cercana
            func_line = -1
            code_between = False
            
            for j in range(i-1, max(0, i-20), -1):
                if 'def ' in lines[j]:
                    func_line = j
                    # Verificar si hay código entre la función y la docstring
                    for k in range(j+1, i):
                        if lines[k].strip() and not lines[k].strip().startswith('#'):
                            # Hay código no-comentario
                            code_between = True
                            break
                    break
            
            if func_line >= 0 and code_between:
                print(f"\n❌ Docstring mal ubicada en línea {i+1}")
                print(f"   Función en línea {func_line+1}")
                print(f"   Hay código entre la función y la docstring")
                
                # Extraer la docstring completa
                docstring_lines = []
                j = i
                while j < len(lines):
                    docstring_lines.append(lines[j])
                    if j > i and '"""' in lines[j]:
                        break
                    j += 1
                
                # Encontrar dónde insertar la docstring (justo después de la definición)
                insert_pos = func_line + 1
                # Buscar el final de la definición de función
                while insert_pos < len(lines) and not lines[insert_pos-1].rstrip().endswith(':'):
                    insert_pos += 1
                
                if insert_pos < i:
                    print(f"✅ Moviendo docstring a línea {insert_pos+1}")
                    
                    # Insertar docstring en la posición correcta
                    indent = len(lines[func_line]) - len(lines[func_line].lstrip())
                    for doc_line in docstring_lines:
                        lines.insert(insert_pos, ' ' * indent + doc_line.lstrip())
                        insert_pos += 1
                    
                    # Eliminar docstring de la posición original
                    for _ in range(len(docstring_lines)):
                        if i + len(docstring_lines) < len(lines):
                            lines.pop(i + len(docstring_lines))
                    
                    fixes += 1
        
        i += 1
    
    # Fix específico para create_macro
    print("\n🔧 Arreglando create_macro específicamente...")
    
    for i in range(len(lines)):
        if 'def create_macro' in lines[i]:
            print(f"📍 create_macro encontrado en línea {i+1}")
            
            # Buscar el final de la definición
            j = i
            while j < len(lines) and not lines[j].rstrip().endswith(':'):
                j += 1
            
            if j < len(lines):
                print(f"   Definición termina en línea {j+1}")
                
                # Si hay código inmediatamente después
                if j+1 < len(lines) and not lines[j+1].strip().startswith('"""'):
                    # Buscar la docstring
                    for k in range(j+1, min(j+20, len(lines))):
                        if lines[k].strip().startswith('"""'):
                            print(f"   Docstring encontrada en línea {k+1}")
                            
                            # Mover todo el código entre la definición y la docstring
                            # DESPUÉS de la docstring
                            code_lines = lines[j+1:k]
                            docstring_start = k
                            
                            # Encontrar el final de la docstring
                            docstring_end = k
                            while docstring_end < len(lines) and not (docstring_end > k and '"""' in lines[docstring_end]):
                                docstring_end += 1
                            
                            if docstring_end < len(lines):
                                # Extraer docstring
                                docstring = lines[k:docstring_end+1]
                                
                                # Reorganizar: def -> docstring -> código
                                new_order = lines[:j+1] + docstring + code_lines + lines[docstring_end+1:]
                                lines = new_order
                                print("✅ Reorganizado: función -> docstring -> código")
                                fixes += 1
                                break
            break
    
    print(f"\n✅ Total de {fixes} correcciones aplicadas")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def quick_test():
    """Test rápido de sintaxis"""
    print("\n🧪 Test rápido de sintaxis...")
    
    import subprocess
    
    result = subprocess.run(
        ['python', '-m', 'py_compile', 'trajectory_hub/core/enhanced_trajectory_engine.py'],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print("✅ ¡SINTAXIS CORRECTA!")
        
        # Test del sistema
        print("\n🚀 Ejecutando test_delta_100.py...")
        result = subprocess.run(['python', 'test_delta_100.py'], 
                              capture_output=True, text=True, timeout=30)
        
        # Buscar porcentaje en el output
        if result.stdout:
            import re
            percentages = re.findall(r'(\d+)%', result.stdout)
            if percentages:
                print(f"\n📊 Sistema de deltas al {percentages[-1]}%")
                
            if '100%' in result.stdout:
                print("\n🎉 ¡SISTEMA 100% FUNCIONAL!")
            elif 'Error' in result.stdout:
                # Mostrar errores
                for line in result.stdout.split('\n'):
                    if 'Error' in line or 'error' in line:
                        print(f"❌ {line}")
                        
    else:
        print(f"❌ Error de sintaxis:\n{result.stderr}")

if __name__ == "__main__":
    print("🔧 FIXING DOCSTRING POSITION")
    print("=" * 60)
    
    fix_docstring_position()
    quick_test()