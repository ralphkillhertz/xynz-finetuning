# === test_manual_rotation.py ===
# 🧪 Test de rotación manual de macros con deltas

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time
import math

def test_manual_rotation():
    """Test de rotación manual con sistema de deltas"""
    print("\n🧪 TEST: Rotación Manual de Macros")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)
    print("✅ Engine creado")
    
    # Crear macro en formación cuadrada
    macro_name = engine.create_macro("rotating_square", source_count=4, 
                                   formation="square", spacing=2.0)
    print(f"✅ Macro '{macro_name}' creado en formación cuadrada")
    
    # Obtener posiciones iniciales
    macro = engine._macros[macro_name]
    source_ids = list(macro.source_ids)
    
    initial_positions = {}
    for sid in source_ids:
        initial_positions[sid] = engine._positions[sid].copy()
        print(f"   Fuente {sid}: posición inicial = {initial_positions[sid]}")
    
    # Configurar rotación manual
    print("\n🔧 Configurando rotación manual...")
    success = engine.set_manual_macro_rotation(
        macro_name,
        pitch=0.0,
        yaw=0.0,
        roll=0.0,
        interpolation_speed=0.05  # Suave
    )
    
    if not success:
        print("❌ Error configurando rotación manual")
        return False
    
    print("✅ Rotación manual configurada")
    
    # Test 1: Rotación en Yaw (giro horizontal)
    print("\n🔄 Test 1: Rotación en Yaw (90 grados)")
    engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2)  # 90 grados
    
    for i in range(30):
        engine.update()
        time.sleep(0.03)
    
    print("\nPosiciones después de rotar 90° en Yaw:")
    for sid in source_ids:
        pos = engine._positions[sid]
        print(f"   Fuente {sid}: {pos}")
    
    # Test 2: Rotación en Pitch
    print("\n🔄 Test 2: Añadiendo rotación en Pitch (45 grados)")
    engine.set_manual_macro_rotation(macro_name, pitch=math.pi/4)  # 45 grados
    
    for i in range(30):
        engine.update()
        time.sleep(0.03)
    
    # Test 3: Rotación completa
    print("\n🔄 Test 3: Rotación completa (roll + cambio de velocidad)")
    engine.set_manual_macro_rotation(
        macro_name, 
        pitch=math.pi/6,    # 30 grados
        yaw=math.pi,        # 180 grados
        roll=math.pi/4,     # 45 grados
        interpolation_speed=0.1  # Más rápido
    )
    
    for i in range(50):
        engine.update()
        time.sleep(0.02)
        
        if i % 10 == 0:
            sid = source_ids[0]
            pos = engine._positions[sid]
            print(f"   Update {i}: Fuente {sid} en {pos}")
    
    # Verificar que las posiciones cambiaron
    print("\n📊 RESULTADOS:")
    print("-" * 40)
    
    all_moved = True
    for sid in source_ids:
        initial = initial_positions[sid]
        current = engine._positions[sid]
        distance = np.linalg.norm(current - initial)
        
        print(f"Fuente {sid}:")
        print(f"  Inicial: {initial}")
        print(f"  Final:   {current}")
        print(f"  Distancia: {distance:.3f} {'✅' if distance > 0.1 else '❌'}")
        
        if distance < 0.1:
            all_moved = False
    
    # Test de toggle
    print("\n🔧 Test de toggle on/off:")
    engine.toggle_manual_macro_rotation(macro_name, False)
    print("   Rotación desactivada")
    
    initial_pos = engine._positions[source_ids[0]].copy()
    for _ in range(10):
        engine.update()
    
    final_pos = engine._positions[source_ids[0]]
    if np.allclose(initial_pos, final_pos):
        print("   ✅ Las fuentes no se mueven cuando está desactivado")
    else:
        print("   ❌ Las fuentes se siguen moviendo")
    
    return all_moved

if __name__ == "__main__":
    if test_manual_rotation():
        print("\n✅ ¡ÉXITO! La rotación manual funciona con deltas")
    else:
        print("\n❌ La rotación manual no funciona correctamente")
