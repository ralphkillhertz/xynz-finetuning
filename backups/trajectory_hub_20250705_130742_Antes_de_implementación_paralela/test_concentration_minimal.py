#!/usr/bin/env python3
"""
test_concentration_minimal.py - Test mínimo del sistema
"""

import sys
import os

# Asegurar que podemos importar trajectory_hub
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("1. Importando módulos...")
try:
    from trajectory_hub.core.motion_components import ConcentrationComponent, ConcentrationMode
    print("   ✅ ConcentrationComponent importado")
except Exception as e:
    print(f"   ❌ Error importando ConcentrationComponent: {e}")
    sys.exit(1)

try:
    from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
    print("   ✅ EnhancedTrajectoryEngine importado")
except Exception as e:
    print(f"   ❌ Error importando EnhancedTrajectoryEngine: {e}")
    sys.exit(1)

print("\n2. Creando engine...")
try:
    engine = EnhancedTrajectoryEngine()
    print("   ✅ Engine creado")
except Exception as e:
    print(f"   ❌ Error creando engine: {e}")
    sys.exit(1)

print("\n3. Creando macro...")
try:
    macro_id = engine.create_macro("test", 5, formation="circle")
    print(f"   ✅ Macro creado: {macro_id}")
except Exception as e:
    print(f"   ❌ Error creando macro: {e}")
    sys.exit(1)

print("\n4. Probando concentración...")
try:
    # Establecer concentración
    result = engine.set_macro_concentration(macro_id, 0.5)
    print(f"   ✅ Concentración establecida: {result}")
    
    # Obtener estado
    state = engine.get_macro_concentration_state(macro_id)
    print(f"   ✅ Estado: factor={state.get('factor', 'N/A')}, enabled={state.get('enabled', False)}")
except Exception as e:
    print(f"   ❌ Error en concentración: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n5. Probando update...")
try:
    for i in range(5):
        engine.update()
    print("   ✅ Updates ejecutados sin errores")
except Exception as e:
    print(f"   ❌ Error en update: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ TODAS LAS PRUEBAS PASARON")
