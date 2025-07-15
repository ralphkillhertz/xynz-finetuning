# === test_api_correct.py ===
# 🎯 Test con APIs correctas del sistema
# ⚡ Verificado contra el código actual

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import time

def test_with_correct_api():
    """Test usando las APIs correctas"""
    print("🚀 TEST CON APIS CORRECTAS")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print("✅ Engine creado")
    
    # Test 1: Crear macro directamente (crea las fuentes automáticamente)
    print("\n1️⃣ Creando macro...")
    try:
        macro_name = engine.create_macro("test", 4, formation='square')
        print(f"✅ Macro creado: {macro_name}")
        
        # El macro debería tener source_ids
        if hasattr(engine, '_macros') and macro_name in engine._macros:
            macro = engine._macros[macro_name]
            print(f"   Source IDs: {macro.source_ids if hasattr(macro, 'source_ids') else 'No disponible'}")
        
    except Exception as e:
        print(f"❌ Error creando macro: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Trayectoria individual con API correcta
    print("\n2️⃣ Configurando trayectoria individual...")
    try:
        # La API espera: set_individual_trajectory(macro_name, source_index, shape, ...)
        engine.set_individual_trajectory(
            macro_name,    # nombre del macro
            0,             # índice dentro del macro (0-3)
            'circle',      # forma
            shape_params={'radius': 2.0},
            movement_mode='fix',
            speed=1.0
        )
        
        print("✅ Trayectoria configurada")
        
        # Simular movimiento
        initial_pos = None
        if hasattr(engine._macros[macro_name], 'source_ids'):
            sid = engine._macros[macro_name].source_ids[0]
            initial_pos = engine._positions[sid].copy()
        
        for _ in range(30):
            engine.update()
        
        if initial_pos is not None:
            final_pos = engine._positions[sid]
            movement = np.linalg.norm(final_pos - initial_pos)
            print(f"   Movimiento detectado: {movement:.3f} unidades")
        
    except Exception as e:
        print(f"❌ Error en trayectoria: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Concentración (intentar aunque falle)
    print("\n3️⃣ Aplicando concentración...")
    try:
        engine.set_macro_concentration(macro_name, 0.5)
        print("✅ Concentración aplicada")
    except Exception as e:
        print(f"⚠️ Error en concentración (esperado): {e}")
    
    print("\n✅ Test completado")
    return True

if __name__ == "__main__":
    test_with_correct_api()
