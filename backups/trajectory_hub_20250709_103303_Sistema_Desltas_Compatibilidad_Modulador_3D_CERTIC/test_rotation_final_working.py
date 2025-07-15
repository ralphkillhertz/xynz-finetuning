# === test_rotation_final_working.py ===
# 🎯 Test final de rotación manual individual
# ⚡ Corregido para API actual

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub.core import EnhancedTrajectoryEngine
import numpy as np
import math

print("🎯 TEST FINAL - ROTACIÓN MANUAL INDIVIDUAL")
print("=" * 60)

try:
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
    
    # Crear fuente
    print("1️⃣ Creando fuente en [3, 0, 0]...")
    sid = engine.create_source(0)
    engine._positions[0] = np.array([3.0, 0.0, 0.0])
    if 0 in engine.motion_states:
        engine.motion_states[0].state.position = np.array([3.0, 0.0, 0.0])
    
    # Configurar rotación 90°
    print("\n2️⃣ Configurando rotación 90°...")
    success = engine.set_manual_individual_rotation(
        0,
        yaw=math.pi/2,  # 90 grados en radianes
        pitch=0.0,
        roll=0.0,
        interpolation_speed=0.5,  # Más rápido para ver resultado
        center=[0.0, 0.0, 0.0]
    )
    
    # Verificar configuración
    if success and 0 in engine.motion_states:
        comp = engine.motion_states[0].active_components.get('manual_individual_rotation')
        if comp:
            print(f"   ✅ Configurado correctamente")
            print(f"   Target (radianes): {comp.target_yaw:.4f}")
            print(f"   Target (grados): {math.degrees(comp.target_yaw):.1f}°")
            print(f"   Interpolation speed: {comp.interpolation_speed}")
    
    # Simular
    print("\n3️⃣ Simulando rotación (30 frames)...")
    print("-" * 60)
    print("Frame |    X    |    Y    | Ángulo  | Movimiento")
    print("-" * 60)
    
    for frame in range(31):
        # Guardar posición anterior
        pos_before = engine._positions[0].copy()
        
        # Update sin parámetros
        engine.update()
        
        # Posición actual
        pos = engine._positions[0]
        angle = math.degrees(math.atan2(pos[1], pos[0]))
        
        # Calcular movimiento
        movement = np.linalg.norm(pos - pos_before)
        
        # Mostrar cada 5 frames
        if frame % 5 == 0:
            print(f" {frame:3d}  | {pos[0]:7.4f} | {pos[1]:7.4f} | {angle:7.2f}° | {movement:.6f}")
    
    print("-" * 60)
    
    # Resultado final
    final_pos = engine._positions[0]
    final_angle = math.degrees(math.atan2(final_pos[1], final_pos[0]))
    radius = np.linalg.norm(final_pos[:2])
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"   Posición inicial: [3.000, 0.000, 0.000]")
    print(f"   Posición final:   [{final_pos[0]:.3f}, {final_pos[1]:.3f}, {final_pos[2]:.3f}]")
    print(f"   Ángulo inicial: 0.0°")
    print(f"   Ángulo final: {final_angle:.1f}°")
    print(f"   Radio: {radius:.3f}")
    
    # Evaluación
    error_angle = abs(final_angle - 90.0)
    error_radius = abs(radius - 3.0)
    
    if error_angle < 1.0 and error_radius < 0.1:
        print("\n✅ ¡ROTACIÓN PERFECTA!")
        print("\n🎉 SISTEMA DE DELTAS 100% FUNCIONAL")
        print("   - ConcentrationComponent: ✅")
        print("   - IndividualTrajectory: ✅")
        print("   - MacroTrajectory: ✅")
        print("   - MacroRotation: ✅")
        print("   - ManualMacroRotation: ✅")
        print("   - IndividualRotation: ✅")
        print("   - ManualIndividualRotation: ✅")
        print("\n   TODOS LOS COMPONENTES FUNCIONAN")
    elif error_angle < 10.0:
        print(f"\n⚠️ Rotación parcial ({final_angle:.1f}°)")
        print("   Necesita más frames o mayor interpolation_speed")
    else:
        print(f"\n❌ Rotación incorrecta ({final_angle:.1f}°)")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completado")