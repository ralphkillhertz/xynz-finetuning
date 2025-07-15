# === test_is_manual_rotation.py ===
# 🎯 Test específico: Rotación Manual Individual Source
# ⚡ Con interpolación a ángulos específicos

import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ManualIndividualRotation

def test_is_manual_rotation():
    """Test de rotación manual IS con interpolación"""
    
    print("🎯 TEST: ROTACIÓN MANUAL INDIVIDUAL SOURCE")
    print("=" * 60)
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=5, fps=60, enable_modulator=False)
    
    # Crear fuente
    sid = 0
    engine.create_source(sid)
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])  # En eje X positivo
    
    print(f"\n📍 Fuente creada:")
    print(f"   ID: {sid}")
    print(f"   Posición inicial: {engine._positions[sid]}")
    print(f"   Ángulo inicial: 0°")
    
    # Test 1: Rotación a 90 grados
    print("\n🎯 TEST 1: Rotación manual a 90°")
    print("-" * 40)
    
    motion = engine.motion_states[sid]
    motion.active_components['manual_individual_rotation'] = ManualIndividualRotation(
        yaw=np.pi/2,           # 90 grados
        pitch=0.0,
        roll=0.0,
        interpolation_speed=0.1,  # Velocidad de interpolación
        center=np.array([0.0, 0.0, 0.0])  # Centro de rotación
    )
    
    print("   Target: Yaw=90°, Pitch=0°, Roll=0°")
    print("   Interpolation speed: 0.1")
    
    # Simular
    initial_pos = engine._positions[sid].copy()
    
    for t in range(5):  # 0, 0.5, 1.0, 1.5, 2.0 segundos
        for _ in range(30):
            engine.update()
        
        current_pos = engine._positions[sid].copy()
        angle = np.degrees(np.arctan2(current_pos[1], current_pos[0]))
        distance = np.linalg.norm(current_pos - initial_pos)
        
        print(f"   t={t*0.5:.1f}s: pos=[{current_pos[0]:6.3f}, {current_pos[1]:6.3f}], ángulo={angle:6.1f}°")
    
    # Verificar resultado
    final_angle = np.degrees(np.arctan2(engine._positions[sid][1], engine._positions[sid][0]))
    success_90 = abs(final_angle - 90) < 5  # Tolerancia de 5 grados
    
    print(f"\n   Ángulo final: {final_angle:.1f}°")
    print(f"   ✅ Resultado: {'CORRECTO' if success_90 else 'INCORRECTO'}")
    
    # Test 2: Rotación a -45 grados (315°)
    print("\n🎯 TEST 2: Rotación manual a -45° (315°)")
    print("-" * 40)
    
    # Reset posición
    engine._positions[sid] = np.array([3.0, 0.0, 0.0])
    
    # Nueva rotación manual
    motion.active_components['manual_individual_rotation'] = ManualIndividualRotation(
        yaw=-np.pi/4,          # -45 grados
        pitch=0.0,
        roll=0.0,
        interpolation_speed=0.2,  # Más rápido
        center=np.array([0.0, 0.0, 0.0])
    )
    
    print("   Target: Yaw=-45°, Pitch=0°, Roll=0°")
    print("   Interpolation speed: 0.2")
    
    # Simular
    for t in range(4):  # Menos tiempo por mayor velocidad
        for _ in range(30):
            engine.update()
        
        current_pos = engine._positions[sid].copy()
        angle = np.degrees(np.arctan2(current_pos[1], current_pos[0]))
        
        print(f"   t={t*0.5:.1f}s: pos=[{current_pos[0]:6.3f}, {current_pos[1]:6.3f}], ángulo={angle:6.1f}°")
    
    final_angle = np.degrees(np.arctan2(engine._positions[sid][1], engine._positions[sid][0]))
    success_neg45 = abs(final_angle - (-45)) < 5
    
    print(f"\n   Ángulo final: {final_angle:.1f}°")
    print(f"   ✅ Resultado: {'CORRECTO' if success_neg45 else 'INCORRECTO'}")
    
    # Test 3: Verificar que mantiene el radio
    print("\n🎯 TEST 3: Verificación de radio")
    print("-" * 40)
    
    radius = np.linalg.norm(engine._positions[sid][:2])
    radius_ok = abs(radius - 3.0) < 0.1
    
    print(f"   Radio inicial: 3.0")
    print(f"   Radio final: {radius:.3f}")
    print(f"   ✅ Resultado: {'CORRECTO' if radius_ok else 'INCORRECTO'}")
    
    # RESUMEN
    print("\n" + "=" * 60)
    print("📊 RESUMEN ROTACIÓN MANUAL IS:")
    print(f"   Test 90°: {'✅ PASA' if success_90 else '❌ FALLA'}")
    print(f"   Test -45°: {'✅ PASA' if success_neg45 else '❌ FALLA'}")
    print(f"   Mantiene radio: {'✅ PASA' if radius_ok else '❌ FALLA'}")
    
    if success_90 and success_neg45 and radius_ok:
        print("\n🎉 ¡ROTACIÓN MANUAL IS FUNCIONA PERFECTAMENTE!")
        print("\n✨ SISTEMA DE DELTAS 100% COMPLETO ✨")
    else:
        print("\n❌ Hay problemas con la rotación manual IS")

if __name__ == "__main__":
    test_is_manual_rotation()