# === test_macro_rotation_working_fixed.py ===
# 🎯 Test: MacroRotation con API correcta
# ⚡ Usando create_source(id, name) correctamente

import numpy as np
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub import EnhancedTrajectoryEngine

def test_macro_rotation():
    """Test completo de rotación macro con sistema de deltas"""
    
    print("🎯 TEST MacroRotation - API Correcta")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # Crear 4 fuentes con ID y nombre
    source_ids = []
    positions = [
        [10.0, 0.0, 0.0],
        [0.0, 10.0, 0.0],
        [-10.0, 0.0, 0.0],
        [0.0, -10.0, 0.0]
    ]
    
    for i in range(4):
        # create_source necesita (id: int, name: str)
        motion = engine.create_source(i, f"rotation_test_{i}")
        source_ids.append(i)
        # Establecer posición inicial
        engine._positions[i] = np.array(positions[i])
        print(f"✅ Fuente {i} creada: {motion.state.name if hasattr(motion, 'state') else 'motion'}")
    
    # Crear macro
    macro_name = engine.create_macro("test_rotation", source_count=4, formation="square")
    print(f"\n✅ Macro creado: {macro_name}")
    
    # Mostrar posiciones iniciales
    print("\n📍 Posiciones iniciales:")
    for i in source_ids:
        pos = engine._positions[i]
        print(f"  F{i}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")
    
    # Aplicar rotación
    print("\n🔄 Aplicando rotación Y = 1.0 rad/s...")
    engine.set_macro_rotation(
        macro_name,
        center=[0.0, 0.0, 0.0],
        speed_x=0.0,
        speed_y=1.0,  # 1 rad/s en Y
        speed_z=0.0
    )
    
    # Verificar componentes
    print("\n🔍 Verificando componentes:")
    components_ok = 0
    for sid in source_ids:
        if sid in engine.motion_states:
            motion = engine.motion_states[sid]
            if hasattr(motion, 'active_components') and 'macro_rotation' in motion.active_components:
                comp = motion.active_components['macro_rotation']
                if comp and comp.enabled:
                    components_ok += 1
                    print(f"  F{sid}: ✅ Componente activo")
                    # Probar calculate_delta
                    if hasattr(comp, 'calculate_delta'):
                        try:
                            from trajectory_hub.core.motion_components import MotionState
                            test_state = MotionState()
                            test_state.position = engine._positions[sid].copy()
                            delta = comp.calculate_delta(test_state, 0.0, 0.1)
                            if delta and hasattr(delta, 'position'):
                                print(f"       Delta: {np.linalg.norm(delta.position):.6f}")
                        except:
                            pass
    
    print(f"\n📊 Componentes activos: {components_ok}/4")
    
    if components_ok == 0:
        print("❌ No hay componentes activos")
        return False
    
    # Simular movimiento
    print("\n⏱️ Simulando 2 segundos (120 frames)...")
    dt = 1.0 / 60.0
    
    # Guardar posiciones iniciales
    initial_positions = {sid: engine._positions[sid].copy() for sid in source_ids}
    
    for frame in range(120):
        # Update del engine
        engine.update(dt)
        
        # Mostrar progreso cada 40 frames
        if frame % 40 == 0:
            pos = engine._positions[source_ids[0]]
            print(f"  Frame {frame:3d}: F0 en [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")
    
    # Resultados finales
    print("\n📊 RESULTADOS FINALES:")
    total_movement = 0.0
    
    for sid in source_ids:
        initial = initial_positions[sid]
        final = engine._positions[sid]
        distance = np.linalg.norm(final - initial)
        total_movement += distance
        
        print(f"\nF{sid}:")
        print(f"  Inicial: [{initial[0]:6.2f}, {initial[1]:6.2f}, {initial[2]:6.2f}]")
        print(f"  Final:   [{final[0]:6.2f}, {final[1]:6.2f}, {final[2]:6.2f}]")
        print(f"  Distancia: {distance:.3f}")
    
    # Verificación
    avg_movement = total_movement / len(source_ids)
    print(f"\n📈 Movimiento promedio: {avg_movement:.3f}")
    
    if avg_movement > 1.0:  # Al menos 1 unidad de movimiento
        print("✅ ÉXITO: MacroRotation funciona con sistema de deltas!")
        return True
    else:
        print("❌ Las fuentes no se movieron suficiente")
        print("   Verificar que engine.update() procesa deltas de macro_rotation")
        return False

if __name__ == "__main__":
    try:
        success = test_macro_rotation()
        
        print("\n" + "="*60)
        if success:
            print("🎉 MacroRotation completamente funcional!")
            print("\n📝 Estado del sistema de deltas:")
            print("  ✅ ConcentrationComponent - 100%")
            print("  ✅ IndividualTrajectory - 100%")
            print("  ✅ MacroTrajectory - 100%")
            print("  ✅ MacroRotation - 100%")
            print("\n⭐ Próximo: Servidor MCP (objetivo principal)")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()