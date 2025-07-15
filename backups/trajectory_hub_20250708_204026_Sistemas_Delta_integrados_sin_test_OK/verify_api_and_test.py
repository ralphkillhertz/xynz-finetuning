# === verify_api_and_test.py ===
# 🔍 Verificar API correcta y crear test funcional
# ⚡ Rotaciones IS

import inspect
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def verify_api():
    """Verificar los parámetros correctos de la API"""
    
    print("🔍 VERIFICANDO API DEL ENGINE")
    print("=" * 60)
    
    # Verificar __init__
    print("\n1. EnhancedTrajectoryEngine.__init__:")
    init_sig = inspect.signature(EnhancedTrajectoryEngine.__init__)
    print(f"   Parámetros: {init_sig}")
    
    # Crear engine con parámetros correctos
    engine = EnhancedTrajectoryEngine()
    
    # Verificar set_individual_rotation
    if hasattr(engine, 'set_individual_rotation'):
        print("\n2. set_individual_rotation:")
        sig = inspect.signature(engine.set_individual_rotation)
        print(f"   Parámetros: {sig}")
    else:
        print("\n❌ No existe set_individual_rotation")
    
    # Verificar set_manual_individual_rotation
    if hasattr(engine, 'set_manual_individual_rotation'):
        print("\n3. set_manual_individual_rotation:")
        sig = inspect.signature(engine.set_manual_individual_rotation)
        print(f"   Parámetros: {sig}")
    else:
        print("\n❌ No existe set_manual_individual_rotation")
    
    return engine

def test_is_rotations():
    """Test con API correcta"""
    
    print("\n\n🎯 TEST ROTACIONES IS CON API CORRECTA")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine()
    
    # Verificar max_sources
    max_sources = getattr(engine, 'max_sources', 64)
    print(f"\n📊 Max sources: {max_sources}")
    
    # Crear algunas fuentes
    print("\n📍 Creando fuentes:")
    positions = [[3,0,0], [0,3,0], [-3,0,0], [0,-3,0]]
    
    for i, pos in enumerate(positions[:4]):
        motion = engine.create_source(i)
        engine._positions[i] = pos
        print(f"   Fuente {i}: {pos}")
    
    # Test rotación algorítmica
    print("\n🔄 Test rotación algorítmica:")
    try:
        # Intentar con los parámetros correctos
        if hasattr(engine, 'set_individual_rotation'):
            # Probar diferentes firmas
            try:
                # Opción 1: source_id, speed_x, speed_y, speed_z
                engine.set_individual_rotation(0, 0, 0, 1.0)
                print("   ✅ Formato: (source_id, speed_x, speed_y, speed_z)")
            except:
                try:
                    # Opción 2: source_id, speeds como dict
                    engine.set_individual_rotation(0, {'x': 0, 'y': 0, 'z': 1.0})
                    print("   ✅ Formato: (source_id, speeds_dict)")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
        else:
            print("   ❌ Método no encontrado")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test rotación manual
    print("\n🎯 Test rotación manual:")
    try:
        if hasattr(engine, 'set_manual_individual_rotation'):
            import numpy as np
            engine.set_manual_individual_rotation(1, np.pi/4, 0, 0, 0.1)
            print("   ✅ Rotación manual configurada")
        else:
            print("   ❌ Método no encontrado")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Simular movimiento
    print("\n📊 Simulando movimiento:")
    initial_pos = engine._positions[0].copy() if hasattr(engine, '_positions') else None
    
    for i in range(60):  # 1 segundo
        engine.update()
    
    if initial_pos is not None:
        final_pos = engine._positions[0]
        import numpy as np
        distance = np.linalg.norm(final_pos - initial_pos)
        print(f"   Distancia recorrida: {distance:.3f}")
        if distance > 0.01:
            print("   ✅ Las fuentes se mueven!")
        else:
            print("   ❌ Las fuentes no se mueven")

if __name__ == "__main__":
    engine = verify_api()
    test_is_rotations()