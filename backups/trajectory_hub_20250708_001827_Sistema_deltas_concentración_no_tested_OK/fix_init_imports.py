#!/usr/bin/env python3
"""
🔧 Fix: Arregla los imports en __init__.py
⚡ Error: create_complex_movement no existe
🎯 Solución: Limpiar imports en __init__.py
"""

def check_init_file():
    """Verifica qué está importando __init__.py"""
    print("🔍 Verificando __init__.py...\n")
    
    init_file = "trajectory_hub/core/__init__.py"
    
    try:
        with open(init_file, 'r') as f:
            content = f.read()
        
        print("📋 Contenido actual de __init__.py:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        
        return content
    except Exception as e:
        print(f"❌ Error leyendo __init__.py: {e}")
        return None

def fix_init_imports():
    """Arregla los imports para que solo incluyan lo que existe"""
    print("\n🔧 Arreglando imports en __init__.py...")
    
    init_file = "trajectory_hub/core/__init__.py"
    
    # Imports que SÍ existen y necesitamos
    correct_imports = '''"""
Core components for Trajectory Hub
"""

from .motion_components import (
    MotionState,
    MotionDelta,
    MotionComponent,
    SourceMotion,
    ConcentrationComponent,
    OrientationModulation,
    IndividualTrajectory,
    MacroTrajectory,
    TrajectoryMovementMode,
    TrajectoryDisplacementMode
)

from .enhanced_trajectory_engine import EnhancedTrajectoryEngine
from .spat_osc_bridge import SpatOSCBridge

__all__ = [
    'MotionState',
    'MotionDelta', 
    'MotionComponent',
    'SourceMotion',
    'ConcentrationComponent',
    'OrientationModulation',
    'IndividualTrajectory',
    'MacroTrajectory',
    'TrajectoryMovementMode',
    'TrajectoryDisplacementMode',
    'EnhancedTrajectoryEngine',
    'SpatOSCBridge'
]
'''
    
    with open(init_file, 'w') as f:
        f.write(correct_imports)
    
    print("✅ __init__.py actualizado con imports correctos")

def verify_all_imports():
    """Verifica que todos los imports funcionen"""
    print("\n🧪 Verificando todos los imports...")
    
    # Lista de imports a verificar
    imports_to_check = [
        ('MotionState', 'trajectory_hub.core.motion_components'),
        ('MotionDelta', 'trajectory_hub.core.motion_components'),
        ('SourceMotion', 'trajectory_hub.core.motion_components'),
        ('ConcentrationComponent', 'trajectory_hub.core.motion_components'),
        ('EnhancedTrajectoryEngine', 'trajectory_hub.core.enhanced_trajectory_engine'),
    ]
    
    all_ok = True
    
    for class_name, module_path in imports_to_check:
        try:
            module = __import__(module_path, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"✅ {class_name}")
            else:
                print(f"❌ {class_name} no encontrado en {module_path}")
                all_ok = False
        except Exception as e:
            print(f"❌ Error importando {class_name}: {e}")
            all_ok = False
    
    return all_ok

def create_final_test():
    """Crea un test final simple"""
    test_code = '''#!/usr/bin/env python3
"""Test final después de arreglar imports"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🧪 TEST FINAL DE IMPORTS\\n")

# Test 1: Import básico
try:
    from trajectory_hub import EnhancedTrajectoryEngine
    print("✅ EnhancedTrajectoryEngine importado")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Clases de motion_components
try:
    from trajectory_hub.core.motion_components import (
        MotionState, MotionDelta, SourceMotion, ConcentrationComponent
    )
    print("✅ Clases de motion_components importadas")
    
    # Crear instancias
    ms = MotionState()
    print(f"   MotionState.position: {ms.position}")
    
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Sistema completo
try:
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
    print("\\n✅ Sistema completo funciona!")
    print(f"   Engine creado con max_sources={engine.max_sources}")
    
except Exception as e:
    print(f"\\n❌ Error creando engine: {e}")

print("\\n✅ Test completado!")
'''
    
    with open("test_imports_final.py", 'w') as f:
        f.write(test_code)
    
    print("\n✅ Test final creado: test_imports_final.py")

def main():
    print("🔧 ARREGLANDO IMPORTS EN __init__.py")
    print("=" * 60)
    
    # 1. Ver qué tiene actualmente
    current = check_init_file()
    
    if current and 'create_complex_movement' in current:
        print("\n⚠️ Encontrado import problemático: create_complex_movement")
    
    # 2. Arreglar
    fix_init_imports()
    
    # 3. Verificar
    if verify_all_imports():
        print("\n✅ TODOS LOS IMPORTS ARREGLADOS")
        create_final_test()
        print("\n📋 Ejecuta ahora:")
        print("$ python test_imports_final.py")
        print("$ python test_delta_system_complete.py")
    else:
        print("\n⚠️ Algunos imports todavía tienen problemas")

if __name__ == "__main__":
    main()