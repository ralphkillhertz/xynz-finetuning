#!/usr/bin/env python3
"""
🚨 FIX DE EMERGENCIA - Corregir error de sintaxis
⚡ Restaurar y aplicar debug correctamente
"""

import os
import shutil

def fix_syntax_error():
    """Corregir el error de sintaxis causado por el debug"""
    
    print("🚨 CORRIGIENDO ERROR DE SINTAXIS\n")
    
    # 1. Restaurar desde backup
    print("1️⃣ Buscando backup más reciente...")
    
    import glob
    backups = sorted(glob.glob("backup_debug_*/enhanced_trajectory_engine.py"))
    
    if backups:
        backup_file = backups[-1]
        print(f"   📁 Restaurando desde: {backup_file}")
        
        engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
        shutil.copy2(backup_file, engine_file)
        
        print("   ✅ Archivo restaurado")
    else:
        print("   ❌ No se encontró backup")
        return False
    
    # 2. Aplicar debug más simple
    print("\n2️⃣ Aplicando debug simplificado...")
    
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Solo agregar prints simples en métodos clave
    
    # En set_macro_concentration
    if 'def set_macro_concentration(self, macro_id: str, factor: float' in content:
        # Buscar el inicio del método y agregar print después de la definición
        import re
        
        # Patrón más seguro
        pattern = r'(def set_macro_concentration\(self, macro_id: str, factor: float.*?\).*?:)\s*\n(\s*)(""".*?""")?'
        
        def add_print(match):
            method_def = match.group(1)
            indent = match.group(2)
            docstring = match.group(3) or ''
            
            if docstring:
                return f'{method_def}\n{indent}{docstring}\n{indent}print(f"🔍 DEBUG: set_macro_concentration - macro={macro_id}, factor={factor}")'
            else:
                return f'{method_def}\n{indent}print(f"🔍 DEBUG: set_macro_concentration - macro={macro_id}, factor={factor}")'
        
        content = re.sub(pattern, add_print, content, count=1, flags=re.DOTALL)
    
    # En update - más simple
    update_pattern = r'(def update\(self.*?\).*?:)\s*\n(\s*)'
    content = re.sub(update_pattern, r'\1\n\2print("🔍 DEBUG: Engine.update() ejecutado")\n\2', content, count=1)
    
    # Guardar
    with open(engine_file, 'w') as f:
        f.write(content)
    
    print("   ✅ Debug aplicado de forma segura")
    
    # 3. Verificar sintaxis
    print("\n3️⃣ Verificando sintaxis...")
    
    try:
        with open(engine_file, 'r') as f:
            compile(f.read(), engine_file, 'exec')
        print("   ✅ Sintaxis correcta")
        return True
    except SyntaxError as e:
        print(f"   ❌ Error de sintaxis: línea {e.lineno}")
        print(f"   {e.text}")
        return False

def create_simple_test():
    """Crear un test más simple que no dependa del engine completo"""
    
    print("\n4️⃣ Creando test alternativo...")
    
    test_code = '''#!/usr/bin/env python3
"""
🧪 Test simplificado - Solo verificar qué clases existen
"""

import os
import sys

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

print("🔍 VERIFICANDO ESTRUCTURA\\n")

# 1. Verificar motion_components
print("1️⃣ Verificando motion_components.py...")
try:
    from trajectory_hub.core import motion_components
    
    # Ver qué clases tiene
    classes = [item for item in dir(motion_components) if item[0].isupper()]
    print(f"   Clases encontradas: {classes}")
    
    # Verificar SourceMotion
    if hasattr(motion_components, 'SourceMotion'):
        sm = motion_components.SourceMotion
        print("\\n   ✅ SourceMotion existe")
        
        # Ver métodos
        methods = [m for m in dir(sm) if not m.startswith('_') and callable(getattr(sm, m, None))]
        print(f"   Métodos: {methods}")
        
        # Verificar get_position
        if 'get_position' in methods:
            print("   ✅ get_position existe en SourceMotion")
        else:
            print("   ❌ get_position NO existe en SourceMotion")
            
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Verificar qué usa el engine
print("\\n2️⃣ Verificando qué clases usa el engine...")

# Leer el archivo directamente
engine_file = "trajectory_hub/core/enhanced_trajectory_engine.py"
if os.path.exists(engine_file):
    with open(engine_file, 'r') as f:
        content = f.read()
    
    # Buscar qué importa
    if 'from trajectory_hub.core.motion_components import' in content:
        import re
        imports = re.findall(r'from trajectory_hub\\.core\\.motion_components import ([^\\n]+)', content)
        print(f"   Importa de motion_components: {imports}")
    
    # Buscar qué crea
    if 'TrajectorySource(' in content:
        print("   → Crea objetos TrajectorySource")
    if 'Source(' in content and 'TrajectorySource' not in content:
        print("   → Crea objetos Source")
    if 'SourceMotion(' in content:
        print("   → Usa SourceMotion directamente")

print("\\n✅ Verificación completada")
'''
    
    with open("test_structure.py", 'w') as f:
        f.write(test_code)
    
    print("   ✅ Test creado: test_structure.py")

if __name__ == "__main__":
    success = fix_syntax_error()
    
    if success:
        print("\n✅ Error corregido")
        create_simple_test()
        
        print("\n🚀 PRÓXIMOS PASOS:")
        print("\n1. Verificar estructura:")
        print("   python test_structure.py")
        print("\n2. Probar con debug:")
        print("   python test_with_debug.py")
    else:
        print("\n❌ No se pudo corregir automáticamente")
        print("\nOPCIONES:")
        print("1. Restaurar backup completo del engine")
        print("2. Revisar manualmente la línea del error")