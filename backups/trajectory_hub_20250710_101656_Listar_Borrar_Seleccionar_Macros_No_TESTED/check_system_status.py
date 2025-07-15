#!/usr/bin/env python3
"""
🔍 Verificador de estado del sistema
"""

import os
import sys
import json

def check_status():
    """Verifica el estado del sistema"""
    
    print("🔍 VERIFICANDO ESTADO DEL SISTEMA")
    print("=" * 50)
    
    checks = {
        "Python Version": sys.version.split()[0],
        "Project Root": os.path.exists("trajectory_hub"),
        "Core Engine": os.path.exists("trajectory_hub/core/enhanced_trajectory_engine.py"),
        "Formation Manager": os.path.exists("trajectory_hub/control/managers/formation_manager.py"),
        "Interactive Controller": os.path.exists("trajectory_hub/interface/interactive_controller.py")
    }
    
    print("\n📋 Verificaciones:")
    all_good = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}: {result}")
        if not result:
            all_good = False
    
    # Test imports
    print("\n🧪 Probando imports...")
    try:
        from trajectory_hub.control.managers.formation_manager import FormationManager
        print("  ✅ FormationManager importa correctamente")
    except Exception as e:
        print(f"  ❌ FormationManager: {e}")
        all_good = False
    
    try:
        from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
        print("  ✅ EnhancedTrajectoryEngine importa correctamente")
    except Exception as e:
        print(f"  ❌ EnhancedTrajectoryEngine: {e}")
        all_good = False
    
    print("\n" + "=" * 50)
    if all_good:
        print("✅ SISTEMA LISTO PARA USAR")
    else:
        print("❌ SISTEMA REQUIERE FIXES")
        print("\n💡 Ejecuta:")
        print("   python fix_imports_definitively.py")
        print("   python fix_trajectory_movement_mode.py")
    
    return all_good

if __name__ == "__main__":
    check_status()
