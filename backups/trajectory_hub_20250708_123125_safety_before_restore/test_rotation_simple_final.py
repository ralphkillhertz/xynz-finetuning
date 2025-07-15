# === test_rotation_simple_final.py ===
# 🔧 Test simple de rotación MS
# ⚡ Sin monkey patching
# 🎯 Impacto: DEBUG

import numpy as np

print("🔍 Test simple de rotación MS")
print("=" * 50)

try:
    from trajectory_hub.core.motion_components import MacroRotation, MotionState
    from trajectory_hub import EnhancedTrajectoryEngine
    
    print("✅ Imports exitosos")
    
    # Test directo de MacroRotation
    print("\n📋 Test 1: MacroRotation directa")
    rotation = MacroRotation()
    
    # Verificar el método set_rotation
    print("   Configurando rotación...")
    rotation.set_rotation(0.0, 1.0, 0.0)
    print(f"   ✅ enabled: {rotation.enabled}")
    print(f"   ✅ speed_x: {rotation.speed_x}")
    print(f"   ✅ speed_y: {rotation.speed_y}")
    print(f"   ✅ speed_z: {rotation.speed_z}")
    
    # Test con el engine
    print("\n📋 Test 2: Con Engine")
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
    
    # Crear fuentes en posiciones específicas
    positions = [
        [2.0, 2.0, 0.0],
        [-2.0, 2.0, 0.0],
        [-2.0, -2.0, 0.0],
        [2.0, -2.0, 0.0]
    ]
    
    for i, pos in enumerate(positions):
        engine.create_source(f"test_{i}")
        engine._positions[i] = np.array(pos)
    
    print("✅ Fuentes creadas")
    
    # Crear macro
    engine.create_macro("rot_test", [0, 1, 2, 3])
    print("✅ Macro creado")
    
    # Posiciones iniciales
    print("\n📍 Posiciones iniciales:")
    for i in range(4):
        print(f"   Fuente {i}: {engine._positions[i]}")
    
    # Aplicar rotación
    print("\n🔄 Aplicando rotación Y = 1.0 rad/s...")
    try:
        engine.set_macro_rotation("rot_test", speed_x=0.0, speed_y=1.0, speed_z=0.0)
        print("✅ Rotación configurada")
    except Exception as e:
        print(f"❌ Error configurando rotación: {e}")
        raise
    
    # Hacer 10 updates
    print("\n⏱️ Ejecutando 10 updates...")
    for i in range(10):
        try:
            engine.update()
            if i == 0:
                print(f"   Frame {i+1}: ✅")
        except Exception as e:
            print(f"   Frame {i+1}: ❌ Error: {e}")
            if "ambiguous" in str(e):
                print("   🚨 ERROR ARRAY AMBIGUOUS!")
                # Inspeccionar el estado
                print("\n   📋 Estado de los componentes:")
                for sid in range(4):
                    if sid in engine.motion_states:
                        motion = engine.motion_states[sid]
                        if 'macro_rotation' in motion.active_components:
                            comp = motion.active_components['macro_rotation']
                            print(f"      Fuente {sid}:")
                            print(f"         enabled: {comp.enabled} (tipo: {type(comp.enabled)})")
                            print(f"         speed_x: {comp.speed_x} (tipo: {type(comp.speed_x)})")
                            print(f"         speed_y: {comp.speed_y} (tipo: {type(comp.speed_y)})")
                            print(f"         speed_z: {comp.speed_z} (tipo: {type(comp.speed_z)})")
            break
    
    # Posiciones finales
    print("\n📍 Posiciones después de 10 frames:")
    for i in range(4):
        initial = np.array(positions[i])
        final = engine._positions[i]
        distance = np.linalg.norm(final - initial)
        print(f"   Fuente {i}: {final} (movió {distance:.3f} unidades)")
    
    # Verificar si hubo movimiento
    total_movement = sum(np.linalg.norm(engine._positions[i] - positions[i]) for i in range(4))
    if total_movement > 0.1:
        print(f"\n✅ Las fuentes se movieron! Total: {total_movement:.3f} unidades")
    else:
        print(f"\n❌ No hubo movimiento suficiente: {total_movement:.3f} unidades")

except Exception as e:
    print(f"\n❌ Error general: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completado")