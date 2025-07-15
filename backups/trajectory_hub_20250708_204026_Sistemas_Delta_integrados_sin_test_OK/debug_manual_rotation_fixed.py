# === debug_manual_rotation_fixed.py ===
# 🔍 Debug corregido para ManualIndividualRotation
# ⚡ Sin usar MotionState directamente

import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ManualIndividualRotation

def debug_manual_rotation():
    """Debug simplificado del problema"""
    
    print("🔍 DEBUG SIMPLIFICADO: ManualIndividualRotation")
    print("=" * 60)
    
    # 1. Crear engine y configurar
    print("\n1️⃣ CREANDO ENGINE Y FUENTE:")
    engine = EnhancedTrajectoryEngine(max_sources=2, fps=60, enable_modulator=False)
    
    sid = 0
    engine.create_source(sid)
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])
    
    print(f"   Posición inicial: {engine._positions[sid]}")
    
    # 2. Configurar rotación manual
    print("\n2️⃣ CONFIGURANDO ROTACIÓN MANUAL:")
    result = engine.set_manual_individual_rotation(sid, yaw=np.pi/2, interpolation_speed=0.9)
    print(f"   Resultado: {result}")
    
    # 3. Obtener componente y estado
    motion = engine.motion_states[sid]
    comp = motion.active_components.get('manual_individual_rotation')
    
    if not comp:
        print("   ❌ No se encontró el componente")
        return
    
    print(f"\n   Estado del componente:")
    print(f"   - Center: {comp.center}")
    print(f"   - Current yaw: {comp.current_yaw:.3f}")
    print(f"   - Target yaw: {comp.target_yaw:.3f} ({np.degrees(comp.target_yaw):.1f}°)")
    print(f"   - Enabled: {comp.enabled}")
    
    # 4. Verificar state
    print(f"\n3️⃣ VERIFICANDO STATE:")
    print(f"   motion.state: {motion.state}")
    print(f"   motion.state.position: {motion.state.position}")
    print(f"   engine._positions[{sid}]: {engine._positions[sid]}")
    
    # 5. Probar update manual
    print("\n4️⃣ PROBANDO UPDATE MANUAL:")
    print("-" * 40)
    
    # Primero, actualizar el current_yaw manualmente
    print("\n   Actualizando current_yaw manualmente:")
    
    for i in range(10):
        # Calcular diferencia de ángulo
        angle_diff = comp.target_yaw - comp.current_yaw
        
        # Normalizar
        while angle_diff > np.pi:
            angle_diff -= 2 * np.pi
        while angle_diff < -np.pi:
            angle_diff += 2 * np.pi
        
        # Aplicar interpolación
        dt = 0.016
        delta_angle = angle_diff * comp.interpolation_speed * dt
        comp.current_yaw += delta_angle
        
        if i % 3 == 0:
            print(f"   Frame {i}: current_yaw = {comp.current_yaw:.3f} ({np.degrees(comp.current_yaw):.1f}°)")
    
    # 6. Calcular posición manualmente
    print("\n5️⃣ CALCULANDO POSICIÓN MANUALMENTE:")
    
    # Posición relativa al centro
    pos = engine._positions[sid]
    relative_pos = pos - comp.center
    distance = np.linalg.norm(relative_pos[:2])
    
    print(f"   Posición actual: {pos}")
    print(f"   Centro: {comp.center}")
    print(f"   Posición relativa: {relative_pos}")
    print(f"   Distancia: {distance:.3f}")
    
    # Nueva posición
    new_x = distance * np.cos(comp.current_yaw) + comp.center[0]
    new_y = distance * np.sin(comp.current_yaw) + comp.center[1]
    new_pos = np.array([new_x, new_y, pos[2]])
    
    print(f"\n   Nueva posición calculada: {new_pos}")
    print(f"   Delta esperado: {new_pos - pos}")
    
    # 7. Verificar calculate_delta del componente
    print("\n6️⃣ VERIFICANDO calculate_delta:")
    
    # Reset current_yaw para test limpio
    comp.current_yaw = 0.0
    
    # IMPORTANTE: Sincronizar state
    motion.state.position = engine._positions[sid].copy()
    
    # Llamar calculate_delta
    delta = comp.calculate_delta(motion.state, 0, 0.016)
    
    print(f"   Delta retornado: {delta}")
    if delta:
        print(f"   Delta.position: {delta.position}")
        print(f"   ¿Es cero?: {np.allclose(delta.position, 0)}")
    
    # 8. Inspeccionar el método calculate_delta
    print("\n7️⃣ INSPECCIONANDO calculate_delta:")
    
    # Ver si podemos obtener el código
    import inspect
    try:
        source = inspect.getsource(comp.calculate_delta)
        lines = source.split('\n')[:10]
        print("   Primeras líneas del método:")
        for i, line in enumerate(lines):
            print(f"   {i}: {line}")
    except:
        print("   No se puede obtener el código fuente")
    
    # 9. Conclusión
    print("\n" + "=" * 60)
    print("📊 DIAGNÓSTICO:")
    
    if np.allclose(comp.current_yaw, 0):
        print("   ❌ current_yaw no se está actualizando en calculate_delta")
    
    if np.allclose(delta.position if delta else [0,0,0], 0):
        print("   ❌ calculate_delta retorna delta cero")
        print("   Posibles causas:")
        print("   - El método update() no se llama antes de calculate_delta")
        print("   - Hay un bug en la lógica de interpolación")
        print("   - El componente no está enabled correctamente")

if __name__ == "__main__":
    debug_manual_rotation()