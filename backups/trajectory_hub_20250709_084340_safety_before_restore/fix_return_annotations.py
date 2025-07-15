# === fix_return_annotations.py ===
# 🔧 Fix: Arreglar anotaciones de retorno mal ubicadas
# ⚡ Líneas con -> tipo: que quedaron sueltas

import os

def fix_return_annotations():
    """Arreglar anotaciones de tipo de retorno mal ubicadas"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_return', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Buscando anotaciones de retorno mal ubicadas...")
    
    # Buscar líneas que empiezan con ->
    lines_to_remove = []
    fixes = 0
    
    for i in range(len(lines)):
        line = lines[i].strip()
        
        # Si la línea empieza con -> o es solo una anotación de tipo
        if line.startswith('->') and line.endswith(':'):
            print(f"❌ Anotación suelta en línea {i+1}: {line}")
            lines_to_remove.append(i)
            
            # Buscar la definición de función más cercana hacia atrás
            j = i - 1
            while j >= 0:
                if 'def ' in lines[j]:
                    # Añadir la anotación a la definición
                    if ')' in lines[j] and not lines[j].rstrip().endswith(':'):
                        lines[j] = lines[j].rstrip() + ' ' + line + '\n'
                        print(f"✅ Movida a línea {j+1}")
                        fixes += 1
                    break
                j -= 1
    
    # Eliminar líneas marcadas
    for idx in sorted(lines_to_remove, reverse=True):
        del lines[idx]
    
    # Buscar otros patrones problemáticos
    print("\n🔍 Buscando otros patrones problemáticos...")
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Si una línea tiene -> pero no es una definición completa
        if '->' in line and line.strip().endswith(':') and 'def' not in line:
            # Verificar contexto
            if i > 0 and not lines[i-1].strip().endswith(')'):
                print(f"❌ Anotación problemática en línea {i+1}: {line.strip()}")
                
                # Si la línea anterior termina con parámetros
                if '=' in lines[i-1] or ',' in lines[i-1]:
                    # Mover la anotación a la línea anterior
                    type_annotation = line.strip()
                    lines[i-1] = lines[i-1].rstrip() + ') ' + type_annotation + '\n'
                    lines.pop(i)
                    print("✅ Fusionada con línea anterior")
                    fixes += 1
                    continue
        
        # Si encontramos algo como "center: Optional[List[float]] = None -> bool:"
        if '=' in line and '->' in line and line.endswith(':'):
            print(f"❌ Línea mixta en {i+1}: {line.strip()[:50]}...")
            # Separar parámetro de anotación
            parts = line.split('->')
            if len(parts) == 2:
                param_part = parts[0].strip()
                return_part = '->' + parts[1].strip()
                
                # Reemplazar línea
                lines[i] = line[:line.index(param_part)] + param_part + ')' + return_part + '\n'
                print("✅ Corregida")
                fixes += 1
        
        i += 1
    
    print(f"\n✅ Total de {fixes} correcciones aplicadas")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def final_syntax_test():
    """Test final completo"""
    print("\n🧪 Test final de sintaxis...")
    
    import subprocess
    
    # Verificar compilación
    result = subprocess.run(
        ['python', '-m', 'py_compile', 'trajectory_hub/core/enhanced_trajectory_engine.py'],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print("✅ ¡SINTAXIS PERFECTA!")
        
        # Ejecutar test completo
        print("\n🚀 EJECUTANDO TEST COMPLETO DEL SISTEMA...")
        print("=" * 60)
        
        result = subprocess.run(['python', 'test_delta_100.py'], 
                              capture_output=True, text=True)
        
        # Mostrar output completo del test
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("\nERRORES:")
            print(result.stderr)
            
        # Resumen
        if '100%' in str(result.stdout):
            print("\n" + "="*60)
            print("🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL! 🎉")
            print("="*60)
            
    else:
        print(f"❌ Todavía hay errores:\n{result.stderr}")
        
        # Extraer número de línea
        import re
        match = re.search(r'line (\d+)', result.stderr)
        if match:
            line_num = int(match.group(1))
            print(f"\n📍 Error en línea {line_num}")
            
            with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
                lines = f.readlines()
            
            for i in range(max(0, line_num-3), min(len(lines), line_num+2)):
                marker = ">>>" if i == line_num-1 else "   "
                print(f"{marker} {i+1}: {lines[i].rstrip()}")

if __name__ == "__main__":
    print("🔧 FIXING RETURN ANNOTATIONS")
    print("=" * 60)
    
    fix_return_annotations()
    final_syntax_test()