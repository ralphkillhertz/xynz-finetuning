# === test_delta_simple.py ===
# 🎯 Test simple del sistema de deltas
# ⚡ Verificación básica post-fixes

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np

def test_simple():
    print("🚀 TEST SIMPLE SISTEMA DE DELTAS")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=20, fps=60)
    
    # Test 1: create_macro retorna objeto
    print("\n1️⃣ TEST: create_macro retorna objeto")
    macro = engine.create_macro("test", 3, formation='line', spacing=2.0)
    
    if hasattr(macro, 'source_ids'):
        print(f"✅ Macro es objeto con source_ids: {macro.source_ids}")
    else:
        print(f"❌ Macro no es objeto: {type(macro)}")
        return
    
    # Test 2: set_individual_rotation con parámetros
    print("\n2️⃣ TEST: set_individual_rotation")
    try:
        sid = 10
        engine.create_source(sid)
        engine.set_individual_rotation(sid, speed_x=0.0, speed_y=1.0, speed_z=0.0)
        print("✅ set_individual_rotation acepta parámetros correctos")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Concentración básica
    print("\n3️⃣ TEST: Concentración")
    try:
        engine.set_macro_concentration(macro, 0.5)
        
        # Simular algunos frames
        for _ in range(10):
            engine.update()
        
        print("✅ Concentración ejecutada sin errores")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Test completado")

if __name__ == "__main__":
    test_simple()
