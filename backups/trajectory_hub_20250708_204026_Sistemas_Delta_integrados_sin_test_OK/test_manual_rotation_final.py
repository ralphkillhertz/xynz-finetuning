import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_manual_rotation():
    """Test completo de rotación manual individual"""
    print("🧪 TEST DEFINITIVO: ROTACIÓN MANUAL INDIVIDUAL")
    print("=" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear engine con parámetros CORRECTOS
        print("1️⃣ Creando engine...")
        engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
        print(f"✅ Engine creado (max_sources={engine.max_sources}, fps={engine.fps})")
        
        # Crear fuente
        print("\n2️⃣ Creando fuente...")
        sid = engine.create_source(0)
        print(f"✅ Fuente creada: {sid}")
        
        # Establecer posición inicial
        initial_pos = np.array([3.0, 0.0, 0.0])
        engine._positions[0] = initial_pos.copy()
        print(f"   Posición inicial: {engine._positions[0]}")
        
        # Configurar rotación manual
        print("\n3️⃣ Configurando rotación manual IS...")
        success = engine.set_manual_individual_rotation(
            source_id=0,
            yaw=90.0,      # grados - rotar 90° en sentido antihorario
            pitch=0.0,
            roll=0.0,
            interpolation_speed=45.0  # grados/segundo = 2 segundos para 90°
        )
        print(f"✅ Rotación configurada: {success}")
        
        # Verificar componente
        print("\n4️⃣ Estado del componente:")
        if 0 in engine.motion_states:
            motion = engine.motion_states[0]
            if 'manual_individual_rotation' in motion.active_components:
                comp = motion.active_components['manual_individual_rotation']
                print(f"   ✅ Componente activo")
                print(f"   - Enabled: {comp.enabled}")
                print(f"   - Current yaw: {np.degrees(comp.current_yaw):.1f}°")
                print(f"   - Target yaw: {np.degrees(comp.target_yaw):.1f}°")
                print(f"   - Speed: {comp.interpolation_speed}°/s")
                print(f"   - Center: {comp.center}")
            else:
                print("   ❌ Componente no encontrado")
                return
        
        # Simular movimiento
        print("\n5️⃣ Simulando movimiento (2 segundos)...")
        print("-" * 50)
        print("Tiempo | Posición [X,Y,Z] | Ángulo | Radio")
        print("-" * 50)
        
        dt = 1.0 / engine.fps
        frames = int(2.0 * engine.fps)  # 2 segundos
        
        positions = []
        for frame in range(frames + 1):
            # Actualizar
            if frame > 0:  # No actualizar en frame 0
                engine.update(dt)
            
            # Obtener posición actual
            pos = engine._positions[0].copy()
            positions.append(pos)
            
            # Calcular métricas
            angle = np.degrees(np.arctan2(pos[1], pos[0]))
            radius = np.linalg.norm(pos[:2])
            
            # Mostrar cada 0.25 segundos
            if frame % (engine.fps // 4) == 0:
                t = frame / engine.fps
                print(f"{t:4.1f}s | [{pos[0]:6.3f}, {pos[1]:6.3f}, {pos[2]:6.3f}] | {angle:6.1f}° | {radius:.3f}")
        
        # Análisis final
        print("\n6️⃣ ANÁLISIS DE RESULTADOS:")
        print("=" * 50)
        
        final_pos = positions[-1]
        expected_pos = np.array([0.0, 3.0, 0.0])  # 90° desde [3,0,0]
        
        # Métricas
        total_movement = np.linalg.norm(final_pos - initial_pos)
        final_angle = np.degrees(np.arctan2(final_pos[1], final_pos[0]))
        final_radius = np.linalg.norm(final_pos[:2])
        position_error = np.linalg.norm(final_pos - expected_pos)
        angle_error = abs(final_angle - 90.0)
        
        print(f"Posición inicial:  [{initial_pos[0]:.3f}, {initial_pos[1]:.3f}, {initial_pos[2]:.3f}]")
        print(f"Posición final:    [{final_pos[0]:.3f}, {final_pos[1]:.3f}, {final_pos[2]:.3f}]")
        print(f"Posición esperada: [{expected_pos[0]:.3f}, {expected_pos[1]:.3f}, {expected_pos[2]:.3f}]")
        print(f"\nMovimiento total: {total_movement:.3f} unidades")
        print(f"Ángulo final: {final_angle:.1f}° (error: {angle_error:.1f}°)")
        print(f"Radio mantenido: {final_radius:.3f} (debe ser 3.000)")
        print(f"Error posición: {position_error:.3f}")
        
        # Verificar si el componente update() se llamó
        if 0 in engine.motion_states:
            motion = engine.motion_states[0]
            if 'manual_individual_rotation' in motion.active_components:
                comp = motion.active_components['manual_individual_rotation']
                print(f"\nEstado final del componente:")
                print(f"- Current yaw: {np.degrees(comp.current_yaw):.1f}°")
                print(f"- Enabled: {comp.enabled} (debe ser False si llegó)")
        
        # Veredicto final
        print("\n" + "=" * 60)
        if total_movement > 3.0 and angle_error < 5.0 and abs(final_radius - 3.0) < 0.1:
            print("✅ ¡ROTACIÓN MANUAL IS FUNCIONA PERFECTAMENTE! 🎉")
            print("   La fuente rotó 90° manteniendo el radio constante")
        elif total_movement > 0.1:
            print("⚠️ La fuente se mueve pero hay problemas:")
            if angle_error > 5.0:
                print("   - No llegó al ángulo objetivo")
            if abs(final_radius - 3.0) > 0.1:
                print("   - El radio no se mantuvo constante")
        else:
            print("❌ La fuente NO se mueve")
            print("   Verifica que el método update() del componente se esté llamando")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_manual_rotation()