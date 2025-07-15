# === fix_line_168.py ===
# 🔧 Fix: Arreglar error de indentación en línea 168
# ⚡ Buscar y corregir el problema específico

import os

def fix_line_168():
    """Arreglar error de indentación en línea 168"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_168', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Analizando error en línea 168...")
    
    # Mostrar contexto
    print("\n📋 Contexto alrededor de línea 168:")
    for i in range(max(0, 160), min(175, len(lines))):
        if i < len(lines):
            marker = ">>>" if i == 167 else "   "
            print(f"{marker} {i+1}: {lines[i].rstrip()}")
    
    # Buscar patrones problemáticos alrededor de línea 168
    fixes = 0
    
    # Verificar si hay una función o estructura que termina sin cuerpo
    for i in range(max(0, 150), min(180, len(lines))):
        if i < len(lines):
            line = lines[i]
            
            # Si encontramos algo que termina con : y requiere indentación
            if line.rstrip().endswith(':') and any(keyword in line for keyword in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except']):
                # Verificar la siguiente línea no vacía
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                
                if j < len(lines):
                    next_line = lines[j]
                    current_indent = len(line) - len(line.lstrip())
                    expected_indent = current_indent + 4
                    actual_indent = len(next_line) - len(next_line.lstrip())
                    
                    # Si la siguiente línea no está correctamente indentada
                    if next_line.strip() and actual_indent <= current_indent:
                        print(f"\n❌ Problema de indentación después de línea {i+1}")
                        print(f"   Línea: {line.strip()}")
                        print(f"   Siguiente: {next_line.strip()}")
                        
                        # Insertar pass si no hay cuerpo
                        if 'def ' in line or 'class ' in line:
                            lines.insert(i+1, ' ' * expected_indent + 'pass  # TODO: implementar\n')
                            print("✅ Añadido 'pass' temporal")
                            fixes += 1
                            break
    
    # Si no encontramos el problema con el método anterior, buscar específicamente en línea 168
    if fixes == 0 and 167 < len(lines):
        print("\n🔧 Analizando línea 168 específicamente...")
        
        # Verificar qué hay antes
        for i in range(max(0, 160), 168):
            if i < len(lines) and lines[i].rstrip().endswith(':'):
                # Esta línea requiere indentación después
                print(f"📍 Línea {i+1} requiere indentación: {lines[i].strip()}")
                
                # Verificar si hay algo indentado después
                has_body = False
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip():
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        expected = len(lines[i]) - len(lines[i].lstrip()) + 4
                        if indent >= expected:
                            has_body = True
                            break
                
                if not has_body:
                    print("❌ No hay cuerpo indentado")
                    indent = len(lines[i]) - len(lines[i].lstrip()) + 4
                    lines.insert(i+1, ' ' * indent + 'pass\n')
                    print("✅ Añadido 'pass'")
                    fixes += 1
    
    # Verificar si el problema es que hay una línea mal cerrada
    if fixes == 0:
        print("\n🔍 Buscando otras causas...")
        
        # Buscar docstrings sin cerrar
        in_docstring = False
        docstring_start = -1
        
        for i in range(max(0, 100), min(180, len(lines))):
            if '"""' in lines[i]:
                if not in_docstring:
                    in_docstring = True
                    docstring_start = i
                else:
                    in_docstring = False
                    
        if in_docstring and docstring_start > 0:
            print(f"❌ Docstring sin cerrar desde línea {docstring_start+1}")
            # Cerrar en línea 167
            if 166 < len(lines):
                lines[166] = lines[166].rstrip() + '"""\n'
                print("✅ Cerrada docstring")
                fixes += 1
    
    print(f"\n✅ Total de {fixes} correcciones aplicadas")
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def quick_test():
    """Test rápido"""
    print("\n🧪 Test rápido...")
    
    import subprocess
    
    result = subprocess.run(
        ['python', '-m', 'py_compile', 'trajectory_hub/core/enhanced_trajectory_engine.py'],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        print("✅ ¡SINTAXIS CORRECTA!")
        
        # Import test
        try:
            print("\n🔍 Verificando import...")
            from trajectory_hub.core import EnhancedTrajectoryEngine
            print("✅ Import exitoso")
            
            # Crear engine
            engine = EnhancedTrajectoryEngine(max_sources=4)
            print("✅ Engine creado")
            
            # Test de deltas
            print("\n🚀 Ejecutando test_delta_100.py...")
            result = subprocess.run(['python', 'test_delta_100.py'], 
                                  capture_output=True, text=True, timeout=30)
            
            # Mostrar resultado
            if result.stdout:
                if '100%' in result.stdout:
                    print("\n🎉 ¡SISTEMA DE DELTAS 100% FUNCIONAL!")
                else:
                    # Buscar porcentaje
                    import re
                    match = re.search(r'(\d+)%', result.stdout)
                    if match:
                        print(f"📊 Sistema al {match.group(1)}%")
                    
                    # Mostrar errores
                    for line in result.stdout.split('\n'):
                        if 'Error:' in line and 'test' not in line.lower():
                            print(f"❌ {line.strip()}")
                            
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {str(e)[:300]}")
            
    else:
        print(f"❌ Error de sintaxis en línea {result.stderr}")
        
        # Mostrar contexto del nuevo error
        import re
        match = re.search(r'line (\d+)', result.stderr)
        if match:
            line_num = int(match.group(1))
            print(f"\n📍 Nuevo error en línea {line_num}")
            
            with open('trajectory_hub/core/enhanced_trajectory_engine.py', 'r') as f:
                lines = f.readlines()
            
            for i in range(max(0, line_num-5), min(len(lines), line_num+3)):
                marker = ">>>" if i == line_num-1 else "   "
                print(f"{marker} {i+1}: {lines[i].rstrip()}")

if __name__ == "__main__":
    print("🔧 FIXING LINE 168 ERROR")
    print("=" * 60)
    
    fix_line_168()
    quick_test()