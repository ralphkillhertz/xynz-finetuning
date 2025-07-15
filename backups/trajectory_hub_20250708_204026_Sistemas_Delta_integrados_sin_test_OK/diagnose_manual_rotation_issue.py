# === diagnose_manual_rotation_issue.py ===
# 🔍 Diagnóstico profundo de por qué no funciona
# ⚡ ManualIndividualRotation

import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ManualIndividualRotation

def diagnose_manual_rotation():
    """Diagnóstico del problema con rotación manual IS"""
    
    print("🔍 DIAGNÓSTICO: ROTACIÓN MANUAL IS")
    print("=" * 60)
    
    # Crear engine y fuente
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60, enable_modulator=False)
    sid = 0
    engine.create_source(sid)
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])
    
    # Configurar rotación manual
    result = engine.set_manual_individual_rotation(sid, yaw=np.pi/2, interpolation_speed=0.5)
    print(f"1️⃣ Configuración: {result}")
    
    # Obtener el componente
    motion = engine.motion_states[sid]
    if 'manual_individual_rotation' in motion.active_components:
        component = motion.active_components['manual_individual_rotation']
        print("\n2️⃣ Estado del componente:")
        print(f"   Target yaw: {component.target_yaw}")
        print(f"   Current yaw: {component.current_yaw}")
        print(f"   Interpolation speed: {component.interpolation_speed}")
        print(f"   Center: {component.center}")
        print(f"   Enabled: {component.enabled}")
        
        # Test manual del calculate_delta
        print("\n3️⃣ Test manual de calculate_delta:")
        
        # Obtener el state
        state = motion.state
        print(f"   State position: {state.position}")
        
        # Llamar calculate_delta manualmente
        try:
            delta = component.calculate_delta(state, 0.0, 0.016)  # 1 frame a 60fps
            print(f"   Delta retornado: {delta}")
            if delta:
                print(f"   Delta.position: {getattr(delta, 'position', 'No tiene')}")
                print(f"   Delta es None: {delta is None}")
        except Exception as e:
            print(f"   ❌ Error en calculate_delta: {e}")
            import traceback
            traceback.print_exc()
        
        # Llamar update manualmente
        print("\n4️⃣ Test manual de update:")
        try:
            component.update(state, 0.0, 0.016)
            print(f"   Current yaw después: {component.current_yaw}")
            print(f"   State position después: {state.position}")
        except Exception as e:
            print(f"   ❌ Error en update: {e}")
        
        # Simular varios frames manualmente
        print("\n5️⃣ Simulación manual de varios frames:")
        for i in range(5):
            # Update del componente
            component.update(state, i * 0.016, 0.016)
            
            # Calculate delta
            delta = component.calculate_delta(state, i * 0.016, 0.016)
            
            print(f"\n   Frame {i}:")
            print(f"   - Current yaw: {component.current_yaw:.3f}")
            print(f"   - State pos: {state.position}")
            print(f"   - Delta: {delta}")
            
            if delta and hasattr(delta, 'position'):
                # Aplicar delta manualmente
                state.position = state.position + delta.position
                print(f"   - Nueva pos: {state.position}")
    
    # Test con engine.update()
    print("\n6️⃣ Test con engine.update():")
    initial = engine._positions[sid].copy()
    
    for i in range(60):  # 1 segundo
        engine.update()
        if i % 20 == 0:
            pos = engine._positions[sid]
            dist = np.linalg.norm(pos - initial)
            print(f"   Frame {i}: pos={pos}, dist={dist:.3f}")
    
    # Verificar diferencia entre state y _positions
    print("\n7️⃣ Verificación state vs _positions:")
    print(f"   motion.state.position: {motion.state.position}")
    print(f"   engine._positions[{sid}]: {engine._positions[sid]}")
    print(f"   ¿Son iguales?: {np.array_equal(motion.state.position, engine._positions[sid])}")
    
    # Conclusión
    print("\n" + "=" * 60)
    print("📊 POSIBLES PROBLEMAS:")
    print("   1. calculate_delta podría estar retornando None")
    print("   2. El delta no se está aplicando correctamente")
    print("   3. Hay desincronización entre state.position y _positions")
    print("   4. El componente no está habilitado o no se actualiza")

if __name__ == "__main__":
    diagnose_manual_rotation()