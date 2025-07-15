# === debug_algorithm_issue.py ===
# 🔍 Debug: Ver exactamente qué está calculando el algoritmo
# ⚡ Muestra paso a paso el cálculo erróneo
# 🎯 Impacto: IDENTIFICAR BUG

import numpy as np

def debug_algorithm():
    """Debug del algoritmo de rotación actual"""
    print("🔍 DEBUG: Algoritmo de calculate_delta")
    print("="*60)
    
    from trajectory_hub.core.motion_components import ManualMacroRotation, MotionState
    
    # Crear componente
    rotation = ManualMacroRotation()
    rotation.enabled = True
    rotation.target_yaw = np.pi/2  # 90 grados
    rotation.interpolation_speed = 1.0
    rotation.center = np.array([0, 0, 0])
    
    # Crear estado de prueba
    state = MotionState()
    state.position = [3.0, 0.0, 0.0]
    
    print("📍 Configuración:")
    print(f"   Posición inicial: {state.position}")
    print(f"   Centro: {rotation.center}")
    print(f"   Target YAW: {np.degrees(rotation.target_yaw)}°")
    print(f"   Velocidad: {rotation.interpolation_speed}")
    
    # Simular calculate_delta paso a paso
    print("\n🧮 Simulando calculate_delta:")
    
    current_position = np.array(state.position)
    relative_pos = current_position - rotation.center
    print(f"   Posición relativa: {relative_pos}")
    
    distance_xy = np.sqrt(relative_pos[0]**2 + relative_pos[1]**2)
    print(f"   Distancia XY: {distance_xy}")
    
    if distance_xy > 0.001:
        current_angle = np.arctan2(relative_pos[1], relative_pos[0])
        print(f"   Ángulo actual: {np.degrees(current_angle)}°")
        
        angle_diff = rotation.target_yaw - current_angle
        print(f"   Diferencia angular: {np.degrees(angle_diff)}°")
        
        # Normalizar
        while angle_diff > np.pi:
            angle_diff -= 2 * np.pi
        while angle_diff < -np.pi:
            angle_diff += 2 * np.pi
        print(f"   Diferencia normalizada: {np.degrees(angle_diff)}°")
        
        dt = 1/60.0
        angle_step = angle_diff * rotation.interpolation_speed * dt
        print(f"   Paso angular (1 frame): {np.degrees(angle_step)}°")
        
        new_angle = current_angle + angle_step
        print(f"   Nuevo ángulo: {np.degrees(new_angle)}°")
        
        new_x = distance_xy * np.cos(new_angle) + rotation.center[0]
        new_y = distance_xy * np.sin(new_angle) + rotation.center[1]
        new_z = relative_pos[2]
        
        new_position = np.array([new_x, new_y, new_z])
        print(f"   Nueva posición calculada: {new_position}")
        
        delta_position = new_position - current_position
        print(f"   Delta: {delta_position}")
    
    # Ahora usar el método real
    print("\n🔧 Usando calculate_delta real:")
    delta = rotation.calculate_delta(state, 0.0, 1/60.0)
    if delta:
        print(f"   Delta real: {delta.position}")
    else:
        print("   ❌ Sin delta")
    
    # Ver qué pasa después de varios pasos
    print("\n📊 Simulando 5 pasos:")
    for i in range(5):
        delta = rotation.calculate_delta(state, i/60.0, 1/60.0)
        if delta and delta.position is not None:
            # Aplicar delta
            state.position[0] += delta.position[0]
            state.position[1] += delta.position[1]
            state.position[2] += delta.position[2]
            
            angle = np.degrees(np.arctan2(state.position[1], state.position[0]))
            dist = np.sqrt(state.position[0]**2 + state.position[1]**2)
            
            print(f"   Paso {i+1}: pos={state.position}, ángulo={angle:.1f}°, dist={dist:.3f}")

if __name__ == "__main__":
    debug_algorithm()