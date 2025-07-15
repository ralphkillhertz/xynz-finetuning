# === fix_create_macro_deep.py ===
# 🔧 Fix: Buscar y corregir todos los returns en create_macro
# ⚡ Solución profunda para el problema del return

import os
import re

def fix_create_macro_returns():
    """Buscar y corregir TODOS los returns en create_macro"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup
    with open(f'{file_path}.backup_create_macro_deep', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Buscar create_macro con regex para encontrar todo el método
    pattern = r'def create_macro\(.*?\):\s*\n(.*?)(?=\n    def|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        print("🔍 Encontrado método create_macro completo")
        method_content = match.group(0)
        
        # Buscar todos los returns
        returns = re.findall(r'return\s+(\w+)', method_content)
        print(f"📋 Returns encontrados: {returns}")
        
        # Reemplazar cada return
        modified_method = method_content
        for ret_var in returns:
            if ret_var in ['name', 'macro_name', 'macro_id']:
                old_return = f'return {ret_var}'
                new_return = f'return self.macros[{ret_var}]'
                modified_method = modified_method.replace(old_return, new_return)
                print(f"✅ Cambiado '{old_return}' por '{new_return}'")
        
        # Reemplazar en el contenido original
        content = content.replace(method_content, modified_method)
        
        # Guardar
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Todos los returns corregidos")
    else:
        print("❌ No se encontró create_macro, buscando línea por línea...")
        
        lines = content.split('\n')
        in_create_macro = False
        indent_level = 0
        
        for i, line in enumerate(lines):
            if 'def create_macro' in line:
                in_create_macro = True
                indent_level = len(line) - len(line.lstrip())
                print(f"🔍 create_macro empieza en línea {i+1}")
            
            if in_create_macro:
                # Si encontramos otra función al mismo nivel, salimos
                if line.strip().startswith('def ') and 'create_macro' not in line:
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= indent_level:
                        in_create_macro = False
                
                # Buscar returns
                if 'return' in line and not line.strip().startswith('#'):
                    print(f"📍 Línea {i+1}: {line.strip()}")
                    
                    # Identificar qué retorna
                    return_match = re.search(r'return\s+([a-zA-Z_]\w*)', line)
                    if return_match:
                        var_name = return_match.group(1)
                        if var_name in ['name', 'macro_name', 'macro_id']:
                            new_line = line.replace(f'return {var_name}', f'return self.macros[{var_name}]')
                            lines[i] = new_line
                            print(f"✅ Línea {i+1} corregida")
        
        # Guardar
        content = '\n'.join(lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def verify_fix():
    """Verificar que el fix funcionó"""
    
    test_code = '''
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine

# Test rápido
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
result = engine.create_macro("test", 2)

print(f"Tipo retornado: {type(result)}")
if hasattr(result, 'source_ids'):
    print(f"✅ ÉXITO: Macro tiene source_ids: {result.source_ids}")
else:
    print(f"❌ FALLO: create_macro retornó: {result}")
'''
    
    # Ejecutar test
    exec(test_code)

def find_actual_return():
    """Buscar el return real en create_macro"""
    
    file_path = 'trajectory_hub/core/enhanced_trajectory_engine.py'
    
    print("\n🔍 BÚSQUEDA PROFUNDA DE RETURNS EN create_macro")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_method = False
    method_indent = 0
    
    for i, line in enumerate(lines):
        if 'def create_macro' in line:
            in_method = True
            method_indent = len(line) - len(line.lstrip())
            print(f"\n📍 create_macro empieza en línea {i+1}")
            print(f"   Indentación: {method_indent}")
        
        if in_method:
            current_indent = len(line) - len(line.lstrip())
            
            # Si encontramos otra definición al mismo nivel, terminamos
            if line.strip().startswith('def ') and current_indent == method_indent and 'create_macro' not in line:
                print(f"\n📍 create_macro termina en línea {i}")
                break
            
            # Mostrar todas las líneas con return
            if 'return' in line and not line.strip().startswith('#'):
                print(f"\n   Línea {i+1}: {line.rstrip()}")
                
                # Si es el return principal (no está en un if/else profundo)
                if current_indent == method_indent + 4:  # Asumiendo 4 espacios de indentación
                    print(f"   ⚠️ ESTE ES EL RETURN PRINCIPAL")
                    
                    # Arreglarlo directamente
                    if 'return name' in line or 'return macro_name' in line:
                        var = 'name' if 'return name' in line else 'macro_name'
                        lines[i] = line.replace(f'return {var}', f'return self.macros[{var}]')
                        print(f"   ✅ CORREGIDO: return self.macros[{var}]")
    
    # Guardar cambios
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

if __name__ == "__main__":
    print("🔧 DEEP FIX FOR create_macro RETURNS")
    print("=" * 60)
    
    print("\n1️⃣ Intentando fix con regex...")
    fix_create_macro_returns()
    
    print("\n2️⃣ Búsqueda profunda de returns...")
    find_actual_return()
    
    print("\n3️⃣ Verificando fix...")
    try:
        verify_fix()
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
    
    print("\n📋 Ejecutar: python test_delta_simple.py")