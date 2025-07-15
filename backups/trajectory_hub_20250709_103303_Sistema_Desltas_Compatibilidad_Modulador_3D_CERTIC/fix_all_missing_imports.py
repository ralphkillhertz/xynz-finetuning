# === fix_all_missing_imports.py ===
# 🔧 Fix: Quitar TODOS los imports que no existen
# ⚡ Limpiar controlador de imports fantasma

def fix_all_imports():
    """Limpiar todos los imports problemáticos"""
    
    # Primero, ver qué está disponible realmente en core
    print("🔍 Verificando qué existe realmente en core/...")
    
    import os
    core_files = []
    core_path = 'trajectory_hub/core'
    
    if os.path.exists(core_path):
        for file in os.listdir(core_path):
            if file.endswith('.py') and not file.startswith('__'):
                core_files.append(file[:-3])  # Sin .py
                print(f"   ✅ {file}")
    
    # Ahora limpiar el controlador
    print("\n🔧 Limpiando imports en interactive_controller.py...")
    
    with open('trajectory_hub/interface/interactive_controller.py', 'r') as f:
        lines = f.readlines()
    
    # Buscar la línea de imports problemática
    for i in range(len(lines)):
        if 'from trajectory_hub.core import' in lines[i] and 'BlendMode' in lines[i]:
            print(f"\n❌ Import problemático en línea {i+1}:")
            print(f"   {lines[i].strip()}")
            
            # Crear una lista de imports válidos basados en archivos existentes
            valid_imports = []
            
            # Imports conocidos que sí existen
            known_good = [
                'EnhancedTrajectoryEngine',
                'TrajectoryDeformer',
                'DeformationType',
                'MacroBehavior',
                'BehaviorMode',
                'DistanceController',
                'SpatOSCBridge'
            ]
            
            # Filtrar solo los que queremos mantener
            current_imports = lines[i].split('import')[1].strip()
            import_list = [imp.strip() for imp in current_imports.split(',')]
            
            for imp in import_list:
                imp_clean = imp.strip().replace('(', '').replace(')', '')
                if imp_clean in known_good:
                    valid_imports.append(imp_clean)
            
            # Reconstruir la línea de import
            if valid_imports:
                new_line = f"from trajectory_hub.core import {', '.join(valid_imports)}\n"
                lines[i] = new_line
                print(f"\n✅ Corregido a:")
                print(f"   {new_line.strip()}")
            else:
                # Si no hay imports válidos, comentar la línea
                lines[i] = f"# {lines[i]}"
                print(f"\n⚠️ Línea comentada")
    
    # Guardar cambios
    with open('trajectory_hub/interface/interactive_controller.py', 'w') as f:
        f.writelines(lines)
    
    # También crear BlendMode como enum simple si se necesita
    print("\n🔧 Creando enums faltantes...")
    
    enum_code = '''# === Agregar al final de motion_components.py ===
from enum import Enum

class BlendMode(Enum):
    """Modos de mezcla para efectos"""
    REPLACE = "replace"
    ADD = "add"
    MULTIPLY = "multiply"
    AVERAGE = "average"
'''
    
    # Verificar si ya existe
    with open('trajectory_hub/core/motion_components.py', 'r') as f:
        content = f.read()
    
    if 'class BlendMode' not in content:
        with open('trajectory_hub/core/motion_components.py', 'a') as f:
            f.write('\n\n' + enum_code)
        print("✅ Añadido BlendMode a motion_components.py")
    
    # Actualizar __init__.py
    with open('trajectory_hub/core/__init__.py', 'r') as f:
        init_content = f.read()
    
    if 'BlendMode' not in init_content:
        # Buscar donde añadirlo
        if 'from .motion_components import' in init_content:
            init_content = init_content.replace(
                'from .motion_components import (',
                'from .motion_components import (BlendMode, '
            )
            
        with open('trajectory_hub/core/__init__.py', 'w') as f:
            f.write(init_content)
        print("✅ Añadido BlendMode a __init__.py")

if __name__ == "__main__":
    fix_all_imports()
    print("\n🚀 Ejecuta: python comprehensive_system_verification.py")