# === debug_rotation_deep.py ===
# 🔍 Debug: Análisis profundo de por qué no rota
# ⚡ Verifica cada paso del algoritmo
# 🎯 Impacto: DIAGNÓSTICO CRÍTICO

import numpy as np
import time

def debug_rotation_algorithm():
    """Debug paso a paso del algoritmo de rotación"""
    print("🔍 DEBUG PROFUNDO: Algoritmo de Rotación Manual")
    print("="*60)
    
    # Importar el sistema
    from trajectory_hub.core import EnhancedTrajectoryEngine
    from trajectory_hub.core.motion_components import ManualMacroRotation
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    
    # Crear macro (retorna el nombre)
    macro_name = engine.create_macro("test_macro", source_count=4, formation="square")
    macro = engine._macros[macro_name]  # Obtener el objeto macro
    print(f"✅ Macro creado con {len(macro.source_ids)} fuentes")
    
    # Establecer posiciones manualmente en el cuadrado
    positions = [
        [3.0, 0.0, 0.0],
        [0.0, 3.0, 0.0],
        [-3.0, 0.0, 0.0],
        [0.0, -3.0, 0.0]
    ]
    
    # Actualizar posiciones directamente en _positions
    for i, (sid, pos) in enumerate(zip(macro.source_ids, positions)):
        engine._positions[sid] = np.array(pos)
        # También actualizar en motion_states
        if sid in engine.motion_states:
            engine.motion_states[sid].position = list(pos)
        print(f"📍 Fuente {sid}: {pos}")
    
    # Crear componente de rotación directamente
    print("\n🔧 Creando ManualMacroRotation...")
    rotation = ManualMacroRotation()
    rotation.enabled = True
    rotation.target_yaw = np.pi/2  # 90 grados
    rotation.interpolation_speed = 0.05
    rotation.center = np.array([0, 0, 0])
    
    # Añadir a todas las fuentes del macro
    for sid in macro.source_ids:
        if sid in engine.motion_states:
            state = engine.motion_states[sid]
            if not hasattr(state, 'active_components'):
                state.active_components = {}
            state.active_components['manual_macro_rotation'] = rotation
            print(f"✅ Rotación añadida a fuente {sid}")
    
    print("\n🎯 Ejecutando 10 pasos de rotación...")
    dt = 1/60.0
    current_time = 0.0
    
    for step in range(10):
        print(f"\n--- Paso {step+1} ---")
        
        # Para cada fuente
        for sid in macro.source_ids:
            state = engine.motion_states[sid]
            
            # Debug del cálculo
            current_position = np.array(state.position)
            relative_pos = current_position - rotation.center
            
            # Ángulo actual
            current_angle = np.arctan2(relative_pos[1], relative_pos[0])
            distance_xy = np.sqrt(relative_pos[0]**2 + relative_pos[1]**2)
            
            print(f"   Fuente {sid}:")
            print(f"      Pos actual: {current_position}")
            print(f"      Ángulo: {np.degrees(current_angle):.1f}°")
            
            # Usar el método real
            delta = rotation.calculate_delta(state, current_time, dt)
            if delta and delta.position is not None:
                print(f"      Delta: {delta.position}")
                
                # Actualizar manualmente
                state.position[0] += delta.position[0]
                state.position[1] += delta.position[1]
                state.position[2] += delta.position[2]
                
                # También actualizar _positions
                engine._positions[sid] = np.array(state.position)
            else:
                print(f"      ⚠️ Sin delta!")
        
        current_time += dt
        
        # Solo mostrar primeros 3 pasos
        if step >= 2:
            break
    
    print("\n📊 Posiciones después de 10 pasos:")
    for sid in macro.source_ids:
        state = engine.motion_states[sid]
        initial = positions[macro.source_ids.index(sid)]
        final = state.position
        distance = np.linalg.norm(np.array(final) - np.array(initial))
        print(f"   Fuente {sid}: {initial} → {final} (movió {distance:.3f})")

def test_with_set_manual():
    """Prueba usando set_manual_macro_rotation del engine"""
    print("\n\n🔍 TEST CON set_manual_macro_rotation")
    print("="*60)
    
    from trajectory_hub.core import EnhancedTrajectoryEngine
    
    engine = EnhancedTrajectoryEngine(max_sources=50, fps=60, enable_modulator=False)
    
    # Crear macro
    macro_name = engine.create_macro("test", source_count=4, formation="square")
    macro = engine._macros[macro_name]
    
    # Posiciones manuales
    positions = [[3,0,0], [0,3,0], [-3,0,0], [0,-3,0]]
    for i, (sid, pos) in enumerate(zip(macro.source_ids, positions)):
        engine._positions[sid] = np.array(pos)
        if sid in engine.motion_states:
            engine.motion_states[sid].position = list(pos)
    
    print("📍 Posiciones iniciales:")
    for sid in macro.source_ids:
        print(f"   Fuente {sid}: {engine._positions[sid]}")
    
    # Configurar rotación manual
    engine.set_manual_macro_rotation("test", yaw=np.pi/2, interpolation_speed=0.5)
    
    # Ejecutar update
    print("\n⚙️ Ejecutando engine.update() 60 veces...")
    for i in range(60):
        engine.update()
        
        # Mostrar progreso cada 20 frames
        if i % 20 == 19:
            print(f"\nFrame {i+1}:")
            for sid in macro.source_ids:
                print(f"   Fuente {sid}: {engine._positions[sid]}")
    
    print("\n📊 Resultado final:")
    for sid in macro.source_ids:
        initial = positions[macro.source_ids.index(sid)]
        final = engine._positions[sid].tolist()
        angle_initial = np.degrees(np.arctan2(initial[1], initial[0]))
        angle_final = np.degrees(np.arctan2(final[1], final[0]))
        print(f"   Fuente {sid}: {initial} → [{final[0]:.2f}, {final[1]:.2f}, {final[2]:.2f}]")
        print(f"      Ángulo: {angle_initial:.1f}° → {angle_final:.1f}°")

if __name__ == "__main__":
    debug_rotation_algorithm()
    test_with_set_manual()