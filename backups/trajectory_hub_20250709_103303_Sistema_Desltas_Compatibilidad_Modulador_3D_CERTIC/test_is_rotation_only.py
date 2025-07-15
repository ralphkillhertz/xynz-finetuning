# === test_is_rotation_only.py ===
# 🎯 Test específico: Solo rotación algorítmica Individual Source
# ⚡ Simple y directo

import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualRotation

def test_is_rotation_algorithmic():
    """Test solo de rotación algorítmica IS"""
    
    print("🎯 TEST: ROTACIÓN ALGORÍTMICA INDIVIDUAL SOURCE")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60, enable_modulator=False)
    
    # Crear una fuente en posición específica
    sid = 0
    engine.create_source(sid)
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])  # En el eje X positivo
    
    print(f"\n📍 Fuente creada:")
    print(f"   ID: {sid}")
    print(f"   Posición inicial: {engine._positions[sid]}")
    
    # Configurar rotación algorítmica directamente
    print("\n🔄 Configurando rotación algorítmica:")
    
    motion = engine.motion_states[sid]
    motion.active_components['individual_rotation'] = IndividualRotation(
        speed_x=0.0,    # Sin rotación en X
        speed_y=0.0,    # Sin rotación en Y  
        speed_z=1.0     # 1 radian/segundo en Z (rotación en plano XY)
    )
    
    print("   Speed X: 0.0 rad/s")
    print("   Speed Y: 0.0 rad/s")
    print("   Speed Z: 1.0 rad/s (rotación en plano XY)")
    
    # Simular movimiento
    print("\n📊 Simulando movimiento:")
    print("-" * 40)
    
    initial_pos = engine._positions[sid].copy()
    
    # Simular cada 0.5 segundos
    for t in range(5):  # 0, 0.5, 1.0, 1.5, 2.0 segundos
        # Simular 30 frames (0.5 segundos a 60 FPS)
        for _ in range(30):
            engine.update()
        
        current_pos = engine._positions[sid].copy()
        distance = np.linalg.norm(current_pos - initial_pos)
        
        # Calcular ángulo actual
        angle = np.arctan2(current_pos[1], current_pos[0])
        angle_degrees = np.degrees(angle)
        
        print(f"   t={t*0.5:.1f}s: pos=[{current_pos[0]:6.3f}, {current_pos[1]:6.3f}, {current_pos[2]:6.3f}]")
        print(f"           ángulo={angle_degrees:6.1f}°, distancia recorrida={distance:6.3f}")
    
    # Verificación final
    print("\n" + "=" * 60)
    final_pos = engine._positions[sid]
    total_distance = np.linalg.norm(final_pos - initial_pos)
    
    # Para 2 segundos a 1 rad/s, debería rotar ~2 radianes (~114.6°)
    expected_angle = np.degrees(2.0)  # 2 radianes a grados
    actual_angle = np.degrees(np.arctan2(final_pos[1], final_pos[0]))
    
    print("📊 RESULTADOS FINALES:")
    print(f"   Posición inicial: {initial_pos}")
    print(f"   Posición final: {final_pos}")
    print(f"   Distancia total recorrida: {total_distance:.3f}")
    print(f"   Ángulo esperado: ~{expected_angle:.1f}°")
    print(f"   Ángulo real: {actual_angle:.1f}°")
    print(f"   Radio mantenido: {np.linalg.norm(final_pos[:2]):.3f} (debería ser ~3.0)")
    
    # Verificar éxito
    success = total_distance > 3.0  # Debería haber recorrido bastante
    radius_maintained = abs(np.linalg.norm(final_pos[:2]) - 3.0) < 0.1
    
    print("\n✅ VERIFICACIÓN:")
    print(f"   ¿Se movió?: {'SÍ' if success else 'NO'}")
    print(f"   ¿Mantuvo el radio?: {'SÍ' if radius_maintained else 'NO'}")
    
    if success and radius_maintained:
        print("\n🎉 ¡ROTACIÓN ALGORÍTMICA IS FUNCIONA PERFECTAMENTE!")
    else:
        print("\n❌ Hay un problema con la rotación")

if __name__ == "__main__":
    test_is_rotation_algorithmic()