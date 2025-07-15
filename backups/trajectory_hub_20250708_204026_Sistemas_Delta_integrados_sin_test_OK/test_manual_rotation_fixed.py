import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_manual_rotation():
    """Test completo de rotación manual individual"""
    print("🧪 TEST DE ROTACIÓN MANUAL INDIVIDUAL")
    print("=" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear engine con parámetros correctos
        print("1️⃣ Creando engine...")
        engine = EnhancedTrajectoryEngine(max_sources=10, update_rate=60)
        print("✅ Engine creado")
        
        # Crear fuente
        print("\n2️⃣ Creando fuente...")
        sid = engine.create_source(0)
        print(f"✅ Fuente creada: {sid}")
        
        # Establecer posición inicial
        engine._positions[0] = np.array([3.0, 0.0, 0.0])
        print(f"   Posición inicial: {engine._positions[0]}")
        
        # Configurar rotación manual
        print("\n3️⃣ Configurando rotación manual...")
        success = engine.set_manual_individual_rotation(
            source_id=0,
            yaw=90.0,      # grados
            pitch=0.0,
            roll=0.0,
            interpolation_speed=45.0  # grados/segundo
        )
        print(f"✅ Rotación configurada: {success}")
        
        # Verificar estado del componente
        print("\n4️⃣ Verificando componente:")
        if 0 in engine.motion_states:
            motion = engine.motion_states[0]
            print(f"   MotionState existe: ✅")
            
            if 'manual_individual_rotation' in motion.active_components:
                comp = motion.active_components['manual_individual_rotation']
                print(f"   Componente existe: ✅")
                print(f"   Enabled: {comp.enabled}")
                print(f"   Current yaw: {np.degrees(comp.current_yaw):.1f}°")
                print(f"   Target yaw: {np.degrees(comp.target_yaw):.1f}°")
                print(f"   Interpolation speed: {comp.interpolation_speed}°/s")
            else:
                print("   ❌ Componente no encontrado en active_components")
                print(f"   Componentes activos: {list(motion.active_components.keys())}")
        else:
            print("   ❌ No hay motion_state para la fuente 0")
        
        # Simular movimiento
        print("\n5️⃣ Simulando 2 segundos de movimiento...")
        print("-" * 40)
        
        positions = []
        dt = 1/60
        
        for frame in range(120):  # 2 segundos a 60 fps
            # Update
            engine.update(dt)
            
            # Guardar posición
            pos = engine._positions[0].copy()
            positions.append(pos)
            
            # Mostrar progreso cada 0.5 segundos
            if frame % 30 == 0:
                t = frame / 60
                angle = np.degrees(np.arctan2(pos[1], pos[0]))
                radius = np.linalg.norm(pos[:2])
                print(f"t={t:.1f}s: pos=[{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}] | ángulo={angle:.1f}° | radio={radius:.2f}")
        
        # Análisis de resultados
        print("\n6️⃣ ANÁLISIS DE RESULTADOS:")
        print("-" * 40)
        
        initial = np.array([3.0, 0.0, 0.0])
        final = positions[-1]
        expected = np.array([0.0, 3.0, 0.0])  # 90 grados
        
        # Métricas
        distance_moved = np.linalg.norm(final - initial)
        final_angle = np.degrees(np.arctan2(final[1], final[0]))
        final_radius = np.linalg.norm(final[:2])
        error_position = np.linalg.norm(final - expected)
        
        print(f"Posición inicial: [{initial[0]:.3f}, {initial[1]:.3f}, {initial[2]:.3f}]")
        print(f"Posición final:   [{final[0]:.3f}, {final[1]:.3f}, {final[2]:.3f}]")
        print(f"Posición esperada: [{expected[0]:.3f}, {expected[1]:.3f}, {expected[2]:.3f}]")
        print(f"\nDistancia total movida: {distance_moved:.3f}")
        print(f"Ángulo final: {final_angle:.1f}° (esperado: 90.0°)")
        print(f"Radio final: {final_radius:.3f} (esperado: 3.000)")
        print(f"Error de posición: {error_position:.3f}")
        
        # Verificar componente después del movimiento
        if 0 in engine.motion_states:
            motion = engine.motion_states[0]
            if 'manual_individual_rotation' in motion.active_components:
                comp = motion.active_components['manual_individual_rotation']
                print(f"\nEstado final del componente:")
                print(f"  Current yaw: {np.degrees(comp.current_yaw):.1f}°")
                print(f"  Enabled: {comp.enabled}")
        
        # Veredicto
        print("\n" + "=" * 60)
        if distance_moved > 0.1 and abs(final_angle - 90.0) < 5.0:
            print("✅ ¡ROTACIÓN MANUAL INDIVIDUAL FUNCIONA PERFECTAMENTE!")
        elif distance_moved > 0.1:
            print("⚠️ La fuente se mueve pero no llega al ángulo correcto")
        else:
            print("❌ La fuente NO se mueve")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_manual_rotation()