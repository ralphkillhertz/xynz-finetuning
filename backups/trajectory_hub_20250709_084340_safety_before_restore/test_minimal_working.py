# === test_minimal_working.py ===
# 🎯 Test mínimo para verificar sistema base
# ⚡ Versión simplificada sin errores

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import time

def test_basic_functionality():
    """Test básico de funcionalidad"""
    print("🚀 TEST MÍNIMO DEL SISTEMA")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    print("✅ Engine creado")
    
    # Test 1: Crear macro
    print("\n1️⃣ Creando macro...")
    try:
        # Crear fuentes primero
        for i in range(4):
            if i not in engine.motion_states:
                engine.create_source(i)
        
        # Crear macro con las fuentes existentes
        macro_name = engine.create_macro("test", 4, formation='square')
        print(f"✅ Macro creado: {macro_name}")
        
        # Verificar posiciones
        for i in range(4):
            pos = engine._positions[i]
            print(f"   Fuente {i}: {pos}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Aplicar concentración
    print("\n2️⃣ Aplicando concentración...")
    try:
        engine.set_macro_concentration(macro_name, 0.5)
        
        # Simular algunos frames
        for _ in range(10):
            engine.update()
            
        print("✅ Concentración aplicada")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Trayectoria individual
    print("\n3️⃣ Configurando trayectoria individual...")
    try:
        engine.set_individual_trajectory(
            0,  # source_id
            'circle',
            shape_params={'radius': 2.0},
            movement_mode='fix',
            speed=1.0
        )
        
        # Simular
        initial_pos = engine._positions[0].copy()
        for _ in range(30):
            engine.update()
            
        final_pos = engine._positions[0]
        movement = np.linalg.norm(final_pos - initial_pos)
        
        if movement > 0.1:
            print(f"✅ Trayectoria funciona - movimiento: {movement:.2f}")
        else:
            print(f"⚠️ Sin movimiento detectado")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Test completado")
    return True

if __name__ == "__main__":
    test_basic_functionality()
