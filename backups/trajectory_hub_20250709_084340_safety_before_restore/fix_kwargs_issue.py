# === fix_kwargs_issue.py ===
# 🔧 Fix: Arreglar definición de función con **kwargs suelto
# ⚡ Línea 256-258 tienen problema estructural

import os

def fix_kwargs_issue():
    """Arreglar **kwargs suelto y definición incompleta"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Backup
    with open(f'{file_path}.backup_kwargs', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("🔍 Analizando contexto del error...")
    
    # Mostrar contexto amplio
    print("\n📋 Contexto alrededor de línea 258:")
    for i in range(max(0, 245), min(265, len(lines))):
        if i < len(lines):
            marker = ">>>" if i in [255, 256, 257] else "   "
            print(f"{marker} {i+1}: {lines[i].rstrip()}")
    
    # Buscar la definición de función más cercana
    func_start = -1
    for i in range(257, -1, -1):
        if i < len(lines) and 'def ' in lines[i]:
            func_start = i
            print(f"\n📍 Función encontrada en línea {i+1}: {lines[i].strip()}")
            break
    
    # Si encontramos la función
    if func_start >= 0:
        # Verificar si la función está bien cerrada
        paren_count = 0
        func_complete = False
        
        for i in range(func_start, min(func_start + 20, len(lines))):
            if i < len(lines):
                paren_count += lines[i].count('(') - lines[i].count(')')
                if lines[i].rstrip().endswith(':') and paren_count == 0:
                    func_complete = True
                    print(f"✅ Función completa en línea {i+1}")
                    break
        
        if not func_complete:
            print("❌ Función incompleta")
            
            # Buscar dónde termina la lista de parámetros
            for i in range(func_start, min(func_start + 30, len(lines))):
                if i < len(lines):
                    line = lines[i].strip()
                    
                    # Si encontramos **kwargs solo
                    if line == '**kwargs':
                        print(f"❌ **kwargs suelto en línea {i+1}")
                        
                        # Buscar si hay más contenido después
                        if i+1 < len(lines) and lines[i+1].strip().startswith('#'):
                            # Añadir ): al final de **kwargs
                            lines[i] = lines[i].rstrip() + '):\n'
                            print("✅ Cerrada definición de función")
                            break
    
    # Fix específico para el problema actual
    if 255 < len(lines) and lines[255].strip() == '**kwargs':
        # Esta línea debería ser parte de una definición de función
        # Verificar línea anterior
        if 254 < len(lines):
            prev_line = lines[254].rstrip()
            if prev_line.endswith(','):
                # Es continuación de parámetros
                indent = len(lines[254]) - len(lines[254].lstrip())
                lines[255] = ' ' * indent + '**kwargs):\n'
                print("✅ Corregido **kwargs con cierre de función")
    
    # Eliminar líneas problemáticas si es necesario
    lines_to_remove = []
    for i in range(len(lines)):
        line = lines[i].strip()
        if line == '-> str:' and i > 0:
            # Esta línea debe ser eliminada o fusionada
            lines_to_remove.append(i)
            print(f"❌ Marcando para eliminar línea {i+1}: {line}")
    
    # Eliminar en orden inverso
    for idx in sorted(lines_to_remove, reverse=True):
        if idx < len(lines):
            del lines[idx]
    
    # Guardar
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ Archivo corregido")

def test_system():
    """Test del sistema completo"""
    print("\n🧪 Verificando sistema...")
    
    import subprocess
    
    # Test de sintaxis
    result = subprocess.run(
        ['python', '-c', 'import ast; ast.parse(open("trajectory_hub/core/enhanced_trajectory_engine.py").read())'],
        capture_output=True, text=True, shell=True
    )
    
    if result.returncode == 0:
        print("✅ ¡SINTAXIS CORRECTA!")
        
        # Ejecutar test completo
        print("\n🚀 EJECUTANDO TEST DEL SISTEMA DE DELTAS...")
        
        result = subprocess.run(['python', 'test_delta_100.py'], 
                              capture_output=True, text=True)
        
        # Mostrar solo las partes importantes
        if result.stdout:
            lines = result.stdout.split('\n')
            
            # Mostrar errores primero
            for line in lines:
                if 'Error' in line or 'error' in line:
                    print(f"❌ {line}")
            
            # Luego el resumen
            show = False
            for line in lines:
                if 'RESUMEN' in line:
                    show = True
                if show or '%' in line:
                    print(line)
        
        if result.returncode != 0 and result.stderr:
            print("\nERRORES:")
            print(result.stderr[-1000:])  # Últimos 1000 chars
            
    else:
        print(f"❌ Error de sintaxis persistente")
        if 'line' in result.stderr:
            import re
            match = re.search(r'line (\d+)', result.stderr)
            if match:
                print(f"   En línea {match.group(1)}")

if __name__ == "__main__":
    print("🔧 FIXING **KWARGS ISSUE")
    print("=" * 60)
    
    fix_kwargs_issue()
    test_system()