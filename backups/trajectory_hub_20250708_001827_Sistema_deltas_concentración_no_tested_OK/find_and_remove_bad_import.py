#!/usr/bin/env python3
"""
🔧 Fix: Encuentra y elimina el import de create_complex_movement
⚡ Error: Algo está importando una función que no existe
🎯 Solución: Buscar en todos los archivos y eliminar
"""

import os
import re

def find_bad_import():
    """Busca dónde se está importando create_complex_movement"""
    print("🔍 Buscando import de 'create_complex_movement'...\n")
    
    # Archivos a revisar
    files_to_check = [
        "trajectory_hub/core/__init__.py",
        "trajectory_hub/core/enhanced_trajectory_engine.py",
        "trajectory_hub/core/motion_components.py",
        "trajectory_hub/core/spat_osc_bridge.py",
        "trajectory_hub/core/distance_controller.py",
        "trajectory_hub/core/trajectory_deformers.py",
        "trajectory_hub/core/macro_behaviors.py",
        "trajectory_hub/__init__.py"
    ]
    
    found_in = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            if 'create_complex_movement' in content:
                print(f"❌ Encontrado en: {file_path}")
                
                # Mostrar contexto
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'create_complex_movement' in line:
                        print(f"   Línea {i+1}: {line.strip()}")
                
                found_in.append(file_path)
        else:
            print(f"⚠️ No existe: {file_path}")
    
    return found_in

def remove_bad_import(file_path):
    """Elimina el import problemático de un archivo"""
    print(f"\n🔧 Arreglando {file_path}...")
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    removed = False
    
    for line in lines:
        if 'create_complex_movement' in line:
            # Comentar la línea en lugar de eliminarla
            new_lines.append(f"# REMOVED: {line}")
            removed = True
            print(f"   ❌ Eliminado: {line.strip()}")
        else:
            new_lines.append(line)
    
    if removed:
        with open(file_path, 'w') as f:
            f.writelines(new_lines)
        print("   ✅ Archivo actualizado")
    
    return removed

def check_circular_imports():
    """Verifica si hay imports circulares"""
    print("\n🔍 Verificando imports circulares...")
    
    # En motion_components.py
    motion_file = "trajectory_hub/core/motion_components.py"
    
    with open(motion_file, 'r') as f:
        content = f.read()
    
    # Buscar imports desde el mismo módulo core
    imports = re.findall(r'from trajectory_hub\.core\.\w+ import', content)
    
    if imports:
        print("⚠️ motion_components.py importa desde otros módulos core:")
        for imp in set(imports):
            print(f"   - {imp}")
        
        return True
    else:
        print("✅ No hay imports circulares evidentes")
        return False

def create_clean_test():
    """Crea un test limpio sin dependencias problemáticas"""
    test_code = '''#!/usr/bin/env python3
"""Test limpio sin imports problemáticos"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🧪 TEST LIMPIO\\n")

# Test 1: Import directo de clases base
print("1️⃣ Importando clases base directamente...")
try:
    # Import directo, no a través de __init__.py
    import trajectory_hub.core.motion_components
    
    # Acceder a las clases
    MotionState = trajectory_hub.core.motion_components.MotionState
    MotionDelta = trajectory_hub.core.motion_components.MotionDelta
    SourceMotion = trajectory_hub.core.motion_components.SourceMotion
    
    print("✅ Clases importadas correctamente")
    
    # Crear instancias
    ms = MotionState()
    print(f"   MotionState position: {ms.position}")
    
    md = MotionDelta()
    print(f"   MotionDelta source: '{md.source}'")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Import del engine
print("\\n2️⃣ Importando EnhancedTrajectoryEngine...")
try:
    import trajectory_hub.core.enhanced_trajectory_engine
    EnhancedTrajectoryEngine = trajectory_hub.core.enhanced_trajectory_engine.EnhancedTrajectoryEngine
    
    print("✅ Engine importado")
    
    # Crear instancia
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
    print(f"   Engine creado: max_sources={engine.max_sources}")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\\n✅ Test completado!")
'''
    
    with open("test_clean_imports.py", 'w') as f:
        f.write(test_code)
    
    print("\n✅ Test limpio creado: test_clean_imports.py")

def main():
    print("🔧 BUSCANDO Y ELIMINANDO IMPORT PROBLEMÁTICO")
    print("=" * 60)
    
    # 1. Buscar dónde está el problema
    files_with_problem = find_bad_import()
    
    if files_with_problem:
        print(f"\n⚠️ Encontrado en {len(files_with_problem)} archivo(s)")
        
        # 2. Eliminar de cada archivo
        for file_path in files_with_problem:
            remove_bad_import(file_path)
    else:
        print("\n✅ No se encontró 'create_complex_movement' en los archivos principales")
    
    # 3. Verificar imports circulares
    check_circular_imports()
    
    # 4. Crear test limpio
    create_clean_test()
    
    print("\n📋 Ejecuta ahora:")
    print("$ python test_clean_imports.py")
    
    print("\nSi aún hay problemas, ejecuta:")
    print("$ grep -r 'create_complex_movement' trajectory_hub/")

if __name__ == "__main__":
    main()