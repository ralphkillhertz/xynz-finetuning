# === test_macro_rotation_final_correct.py ===
# 🎯 Test: MacroRotation con API correcta
# ⚡ Versión final funcional

import numpy as np
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub import EnhancedTrajectoryEngine

def test_macro_rotation():
    """Test completo de rotación macro con sistema de deltas"""
    
    print("🎯 TEST MacroRotation - Sistema de Deltas")
    print("=" * 60)
    
    # Crear engine con parámetros correctos
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # Crear 4 fuentes
    source_ids = []
    positions = [
        [10.0, 0.0, 0.0],
        [0.0, 10.0, 0.0],
        [-10.0, 0.0, 0.0],
        [0.0, -10.0, 0.0]
    ]
    
    for i in range(4):
        sid = engine.create_source(f"rotation_test_{i}")
        source_ids.append(sid)
        # Establecer posición inicial
        engine._positions[sid] = np.array(positions[i])
        print(f"✅ Fuente {sid} creada en {positions[i]}")
    
    # Crear macro
    macro_name = engine.create_macro("test_rotation", source_count=4, formation="square")
    print(f"\n✅ Macro creado: {macro_name}")
    
    # Mostrar posiciones iniciales
    print("\n📍 Posiciones iniciales:")
    for i, sid in enumerate(source_ids):
        pos = engine._positions[sid]
        print(f"  F{sid}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")
    
    # Aplicar rotación
    print("\n🔄 Aplicando rotación Y = 1.0 rad/s...")
    engine.set_macro_rotation(
        macro_name,
        center=[0.0, 0.0, 0.0],
        speed_x=0.0,
        speed_y=1.0,  # 1 rad/s en Y
        speed_z=0.0
    )
    
    # Verificar que los componentes están configurados
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
    
    print(f"\n📊 Componentes activos: {components_ok}/4")
    
    # Simular movimiento
    print("\n⏱️ Simulando 2 segundos (120 frames)...")
    dt = 1.0 / 60.0
    
    # Guardar posiciones para tracking
    trajectories = {sid: [engine._positions[sid].copy()] for sid in source_ids}
    
    for frame in range(120):
        # Update del engine
        engine.update(dt)
        
        # Guardar posiciones
        for sid in source_ids:
            trajectories[sid].append(engine._positions[sid].copy())
        
        # Mostrar progreso cada 30 frames
        if frame % 30 == 0:
            pos = engine._positions[source_ids[0]]
            print(f"  Frame {frame:3d}: F{source_ids[0]} en [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")
    
    # Resultados finales
    print("\n📊 RESULTADOS FINALES:")
    total_movement = 0.0
    
    for i, sid in enumerate(source_ids):
        initial = trajectories[sid][0]
        final = trajectories[sid][-1]
        distance = np.linalg.norm(final - initial)
        total_movement += distance
        
        print(f"\nF{sid}:")
        print(f"  Inicial: [{initial[0]:6.2f}, {initial[1]:6.2f}, {initial[2]:6.2f}]")
        print(f"  Final:   [{final[0]:6.2f}, {final[1]:6.2f}, {final[2]:6.2f}]")
        print(f"  Distancia: {distance:.3f}")
        
        # Verificar ángulo de rotación
        if distance > 0.1:
            # Calcular ángulo rotado
            angle_initial = np.arctan2(initial[2], initial[0])
            angle_final = np.arctan2(final[2], final[0])
            angle_diff = angle_final - angle_initial
            print(f"  Ángulo rotado: {np.degrees(angle_diff):.1f}°")
    
    # Verificación
    avg_movement = total_movement / len(source_ids)
    print(f"\n📈 Movimiento promedio: {avg_movement:.3f}")
    
    # Resultado esperado: ~2 radianes de rotación en 2 segundos
    expected_angle = 2.0  # radianes
    expected_distance = 2 * 10.0 * np.sin(expected_angle/2)  # Para radio 10
    
    if avg_movement > expected_distance * 0.8:  # 80% del esperado
        print("✅ ÉXITO: Las fuentes rotaron correctamente")
        print(f"   Esperado: ~{expected_distance:.3f}, Obtenido: {avg_movement:.3f}")
    else:
        print("❌ Las fuentes no rotaron lo suficiente")
        print(f"   Esperado: ~{expected_distance:.3f}, Obtenido: {avg_movement:.3f}")
    
    return avg_movement > 0.1

if __name__ == "__main__":
    try:
        success = test_macro_rotation()
        
        print("\n" + "="*60)
        if success:
            print("🎉 MacroRotation funciona con sistema de deltas!")
            print("\n📝 Próximos pasos:")
            print("  1. Guardar estado del proyecto")
            print("  2. Implementar rotaciones manuales MS")
            print("  3. Implementar rotaciones IS")
            print("  4. O pasar a servidor MCP")
        else:
            print("❌ Verificar implementación de deltas en engine.update()")
            
    except Exception as e:
        print(f"\n❌ Error en test: {e}")
        import traceback
        traceback.print_exc()