# === debug_manual_rotation_delta.py ===
# 🔍 Debug profundo del calculate_delta
# ⚡ Por qué no genera movimiento

import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ManualIndividualRotation, MotionState

def debug_calculate_delta():
    """Debug profundo del método calculate_delta"""
    
    print("🔍 DEBUG: calculate_delta de ManualIndividualRotation")
    print("=" * 60)
    
    # 1. Test directo del componente
    print("\n1️⃣ TEST DIRECTO DEL COMPONENTE:")
    print("-" * 40)
    
    # Crear componente
    comp = ManualIndividualRotation()
    print(f"   Center: {comp.center}")
    print(f"   Current yaw: {comp.current_yaw}")
    
    # Configurar rotación
    comp.target_yaw = np.pi/2  # 90 grados
    comp.interpolation_speed = 0.5
    comp.enabled = True
    
    print(f"\n   Configuración:")
    print(f"   - Target yaw: {comp.target_yaw} ({np.degrees(comp.target_yaw)}°)")
    print(f"   - Interpolation speed: {comp.interpolation_speed}")
    print(f"   - Enabled: {comp.enabled}")
    
    # Crear un state falso
    state = MotionState(source_id=0)
    state.position = np.array([3.0, 0.0, 0.0])
    
    print(f"\n   State position: {state.position}")
    
    # 2. Llamar calculate_delta paso a paso
    print("\n2️⃣ EJECUTANDO calculate_delta PASO A PASO:")
    print("-" * 40)
    
    # Simular actualización de current_yaw
    print("\n   Actualizando current_yaw...")
    dt = 0.016
    angle_diff = comp.target_yaw - comp.current_yaw
    print(f"   - Diferencia de ángulo: {angle_diff} ({np.degrees(angle_diff)}°)")
    
    # Normalizar ángulo
    while angle_diff > np.pi:
        angle_diff -= 2 * np.pi
    while angle_diff < -np.pi:
        angle_diff += 2 * np.pi
    print(f"   - Diferencia normalizada: {angle_diff}")
    
    # Interpolar
    delta_angle = angle_diff * comp.interpolation_speed * dt
    print(f"   - Delta ángulo (speed * dt): {delta_angle}")
    
    comp.current_yaw += delta_angle
    print(f"   - Nuevo current_yaw: {comp.current_yaw}")
    
    # 3. Calcular nueva posición
    print("\n3️⃣ CALCULANDO NUEVA POSICIÓN:")
    print("-" * 40)
    
    relative_pos = state.position - comp.center
    print(f"   Posición relativa al centro: {relative_pos}")
    
    distance = np.linalg.norm(relative_pos[:2])
    print(f"   Distancia al centro: {distance}")
    
    if distance > 0.001:
        # Calcular nueva posición
        new_x = distance * np.cos(comp.current_yaw) + comp.center[0]
        new_y = distance * np.sin(comp.current_yaw) + comp.center[1]
        new_pos = np.array([new_x, new_y, state.position[2]])
        
        print(f"   Nueva posición calculada: {new_pos}")
        
        # Delta
        position_delta = new_pos - state.position
        print(f"   Delta posición: {position_delta}")
    else:
        print("   ❌ Distancia muy pequeña, no se calcula delta")
    
    # 4. Llamar al método real
    print("\n4️⃣ LLAMANDO AL MÉTODO REAL:")
    print("-" * 40)
    
    # Reset para test limpio
    comp.current_yaw = 0.0
    
    for i in range(5):
        delta = comp.calculate_delta(state, i * dt, dt)
        print(f"\n   Iteración {i}:")
        print(f"   - Current yaw: {comp.current_yaw}")
        print(f"   - Delta: {delta}")
        if delta:
            print(f"   - Delta.position: {delta.position}")
            # Actualizar state para siguiente iteración
            state.position = state.position + delta.position
            print(f"   - Nueva state.position: {state.position}")
    
    # 5. Test con engine completo
    print("\n5️⃣ TEST CON ENGINE COMPLETO:")
    print("-" * 40)
    
    engine = EnhancedTrajectoryEngine(max_sources=1, enable_modulator=False)
    sid = 0
    engine.create_source(sid)
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])
    
    # Configurar
    engine.set_manual_individual_rotation(sid, yaw=np.pi/2, interpolation_speed=0.9)
    
    # Obtener componente
    motion = engine.motion_states[sid]
    comp = motion.active_components.get('manual_individual_rotation')
    
    if comp:
        print(f"   Componente encontrado")
        print(f"   - Center: {comp.center}")
        print(f"   - Current yaw: {comp.current_yaw}")
        print(f"   - Target yaw: {comp.target_yaw}")
        
        # Forzar sincronización
        motion.state.position = engine._positions[sid].copy()
        
        # Test manual
        print("\n   Probando cálculo manual:")
        for i in range(3):
            # Sincronizar
            motion.state.position = engine._positions[sid].copy()
            
            # Calcular delta
            delta = comp.calculate_delta(motion.state, i * 0.016, 0.016)
            
            print(f"\n   Frame {i}:")
            print(f"   - State pos: {motion.state.position}")
            print(f"   - Delta: {delta.position if delta else 'None'}")
            
            if delta and np.any(delta.position != 0):
                print("   ✅ ¡Delta no cero encontrado!")
                break

if __name__ == "__main__":
    debug_calculate_delta()