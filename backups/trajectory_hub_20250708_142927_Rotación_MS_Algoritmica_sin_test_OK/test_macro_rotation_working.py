#!/usr/bin/env python3
"""Test final de MacroRotation que debe funcionar"""

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎯 TEST FINAL MacroRotation - Versión Definitiva")
print("=" * 60)

# 1. Crear engine y macro
engine = EnhancedTrajectoryEngine()
macro_name = engine.create_macro("rotation_test", source_count=4, formation="square", spacing=4.0)
print(f"✅ Macro creado: {macro_name}")

# 2. Verificar posiciones iniciales
print("\n📍 Posiciones iniciales:")
initial_positions = {}
for i in range(4):
    pos = engine._positions[i].copy()
    initial_positions[i] = pos
    print(f"  F{i}: [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")

# 3. Aplicar rotación
print("\n🔄 Aplicando rotación Y = 1.0 rad/s...")
success = engine.set_macro_rotation(macro_name, speed_y=1.0)
print(f"  Configuración: {'✅ Exitosa' if success else '❌ Falló'}")

# 4. Debug componentes
if success:
    print("\n🔍 Verificando componentes:")
    for i in range(4):
        if i in engine.motion_states:
            motion = engine.motion_states[i]
            if 'macro_rotation' in motion.active_components:
                rot = motion.active_components['macro_rotation']
                print(f"  F{i}: enabled={rot.enabled}, speed_y={rot.speed_y}")
                
                # Verificar que tenga calculate_delta
                if hasattr(rot, 'calculate_delta'):
                    # Test rápido
                    delta = rot.calculate_delta(motion, 0, 0.016)
                    print(f"       calculate_delta: ✅ (delta={delta.position if hasattr(delta, 'position') else 'None'})")
                else:
                    print(f"       calculate_delta: ❌ NO EXISTE")

# 5. Simular
print("\n⏱️ Simulando 60 frames (1 segundo)...")
for frame in range(60):
    engine.update()
    
    # Mostrar progreso
    if frame % 20 == 0:
        pos = engine._positions[0]
        print(f"  Frame {frame}: F0 en [{pos[0]:6.2f}, {pos[1]:6.2f}, {pos[2]:6.2f}]")

# 6. Verificar resultados
print("\n📊 RESULTADOS:")
total_movement = 0.0

for i in range(4):
    initial = initial_positions[i]
    final = engine._positions[i]
    distance = np.linalg.norm(final - initial)
    total_movement += distance
    
    print(f"\nF{i}:")
    print(f"  Inicial: [{initial[0]:6.2f}, {initial[1]:6.2f}, {initial[2]:6.2f}]")
    print(f"  Final:   [{final[0]:6.2f}, {final[1]:6.2f}, {final[2]:6.2f}]")
    print(f"  Distancia: {distance:.3f}")
    
    # Calcular ángulo de rotación
    if distance > 0.01:
        angle = np.arctan2(final[2] - initial[2], final[0] - initial[0])
        print(f"  Ángulo: {np.degrees(angle):.1f}°")

avg_movement = total_movement / 4
print(f"\n📈 Movimiento promedio: {avg_movement:.3f}")

# 7. Veredicto
if avg_movement > 0.5:
    print("\n✅ ¡ÉXITO TOTAL! MacroRotation funciona perfectamente")
    print("   El sistema de deltas está operativo")
else:
    print("\n❌ Sin movimiento suficiente")
    print("   Verificar el procesamiento de deltas en engine.update()")
