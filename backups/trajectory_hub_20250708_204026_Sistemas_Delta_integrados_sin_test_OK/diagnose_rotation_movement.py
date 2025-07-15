import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def diagnose_rotation():
    """Diagnóstico profundo del sistema de rotación"""
    print("🔍 DIAGNÓSTICO PROFUNDO: ROTACIÓN MANUAL IS")
    print("=" * 60)
    
    try:
        from trajectory_hub.core import EnhancedTrajectoryEngine
        import numpy as np
        
        # Crear engine
        engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
        sid = engine.create_source(0)
        engine._positions[0] = np.array([3.0, 0.0, 0.0])
        
        print("1️⃣ Sistema creado:")
        print(f"   Fuente 0 en posición: {engine._positions[0]}")
        
        # Configurar rotación
        success = engine.set_manual_individual_rotation(
            source_id=0,
            yaw=90.0,
            pitch=0.0,
            roll=0.0,
            interpolation_speed=45.0
        )
        
        print(f"\n2️⃣ Rotación configurada: {success}")
        
        # Verificar motion state
        if 0 not in engine.motion_states:
            print("❌ No hay motion_state para fuente 0")
            return
            
        motion = engine.motion_states[0]
        print(f"   MotionState existe: ✅")
        print(f"   Active components: {list(motion.active_components.keys())}")
        
        # Verificar componente
        if 'manual_individual_rotation' not in motion.active_components:
            print("❌ No hay componente manual_individual_rotation")
            return
            
        comp = motion.active_components['manual_individual_rotation']
        print(f"\n3️⃣ Estado del componente:")
        print(f"   Clase: {comp.__class__.__name__}")
        print(f"   Enabled: {comp.enabled}")
        print(f"   Current angles: yaw={np.degrees(comp.current_yaw):.1f}°")
        print(f"   Target angles: yaw={np.degrees(comp.target_yaw):.1f}°")
        print(f"   Speed: {np.degrees(comp.interpolation_speed):.1f}°/s")
        
        # Test manual del componente update
        print(f"\n4️⃣ Test manual de component.update():")
        
        # Estado antes
        print(f"   Antes: current_yaw = {np.degrees(comp.current_yaw):.1f}°")
        
        # Llamar update manualmente
        state_before = motion.state
        state_after = comp.update(0.1, 1/60, motion.state)
        
        print(f"   Después: current_yaw = {np.degrees(comp.current_yaw):.1f}°")
        print(f"   ¿Cambió?: {comp.current_yaw != 0}")
        
        # Test calculate_delta
        print(f"\n5️⃣ Test calculate_delta():")
        delta = comp.calculate_delta(motion.state, 0.1, 1/60)
        
        if delta is None:
            print("   ❌ calculate_delta retornó None")
        else:
            print(f"   ✅ Delta retornado: {delta}")
            print(f"   Delta position: {delta.position}")
            print(f"   ¿Es cero?: {np.allclose(delta.position, 0)}")
        
        # Verificar el flujo completo
        print(f"\n6️⃣ Verificando flujo completo en engine.update():")
        
        # Añadir debug hooks
        original_update = motion.update
        update_called = [False]
        
        def debug_update(*args, **kwargs):
            update_called[0] = True
            print("   ⚡ motion.update() fue llamado")
            return original_update(*args, **kwargs)
        
        motion.update = debug_update
        
        # Llamar engine.update
        pos_before = engine._positions[0].copy()
        engine.update()
        pos_after = engine._positions[0].copy()
        
        print(f"   motion.update llamado: {update_called[0]}")
        print(f"   Posición antes: {pos_before}")
        print(f"   Posición después: {pos_after}")
        print(f"   ¿Se movió?: {not np.array_equal(pos_before, pos_after)}")
        
        # Verificar si engine.update llama a motion.update
        print(f"\n7️⃣ Inspeccionando engine.update():")
        
        # Buscar en el código
        import inspect
        engine_update_code = inspect.getsource(engine.update)
        
        checks = [
            ("motion.update", "motion.update" in engine_update_code),
            ("motion_states", "motion_states" in engine_update_code),
            ("calculate_delta", "calculate_delta" in engine_update_code),
            ("active_components", "active_components" in engine_update_code)
        ]
        
        for check, found in checks:
            print(f"   {check}: {'✅' if found else '❌'}")
        
        # Conclusión
        print(f"\n" + "=" * 60)
        print("📊 DIAGNÓSTICO:")
        
        if not update_called[0]:
            print("❌ El problema es que engine.update() no llama a motion.update()")
            print("   Solución: Modificar engine.update() para procesar motion_states")
        elif np.allclose(delta.position if delta else [0,0,0], 0):
            print("❌ calculate_delta retorna delta cero")
            print("   Solución: Revisar la lógica de calculate_delta")
        else:
            print("❓ Problema no identificado claramente")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_rotation()