# === debug_source_1.py ===
# 🔍 Debug: ¿Por qué la fuente 1 no se mueve?
# ⚡ Análisis detallado del problema

import sys
import os
import numpy as np
import math

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from trajectory_hub.core import EnhancedTrajectoryEngine

print("🔍 DEBUG: ¿Por qué la fuente 1 no se mueve?")
print("=" * 60)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60, enable_modulator=False)

# Crear macro
engine.create_macro("test", 4, formation="square")
macro_name = list(engine._macros.keys())[0]
macro = engine._macros[macro_name]

# Posiciones
positions = [[3, 0, 0], [0, 3, 0], [-3, 0, 0], [0, -3, 0]]
for i, (sid, pos) in enumerate(zip(sorted(macro.source_ids), positions)):
    engine._positions[sid] = np.array(pos, dtype=np.float32)

print("Posiciones iniciales:")
for sid in sorted(macro.source_ids):
    print(f"  Fuente {sid}: {engine._positions[sid]}")

# Configurar rotación
engine.set_manual_macro_rotation(macro_name, yaw=math.pi/2, pitch=0, roll=0, interpolation_speed=0.1)

# Obtener el componente de rotación para cada fuente
print("\n🔍 ANALIZANDO COMPONENTES:")
print("-" * 40)

for sid in sorted(macro.source_ids):
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        if hasattr(motion, 'active_components') and 'manual_macro_rotation' in motion.active_components:
            comp = motion.active_components['manual_macro_rotation']
            
            print(f"\nFuente {sid}:")
            print(f"  Posición: {engine._positions[sid]}")
            print(f"  Componente enabled: {comp.enabled}")
            print(f"  Target yaw: {comp.target_yaw:.3f} rad")
            print(f"  Current yaw: {comp.current_yaw:.3f} rad")
            
            # Calcular delta manualmente
            state = motion.state
            state.position = engine._positions[sid].copy()
            
            delta = comp.calculate_delta(state, 0.0, 0.016)
            
            if delta and delta.position is not None:
                print(f"  Delta calculado: {delta.position}")
                print(f"  Magnitud: {np.linalg.norm(delta.position):.6f}")
            else:
                print("  ❌ Delta es None o sin posición")

# Hacer varios updates para ver la progresión
print("\n📊 PROGRESIÓN EN 5 UPDATES:")
print("-" * 40)

for update_num in range(5):
    print(f"\nUpdate {update_num + 1}:")
    
    # Guardar posiciones antes
    pos_before = {sid: engine._positions[sid].copy() for sid in macro.source_ids}
    
    # Update
    engine.update()
    
    # Mostrar cambios
    for sid in sorted(macro.source_ids):
        before = pos_before[sid]
        after = engine._positions[sid]
        diff = np.linalg.norm(after - before)
        
        if diff > 0.0001:
            print(f"  Fuente {sid}: movió {diff:.6f}")
        else:
            print(f"  Fuente {sid}: SIN MOVIMIENTO ❌")

# Análisis final
print("\n🔍 ANÁLISIS FINAL:")
print("-" * 40)

# Revisar si hay algo especial con la posición [0, 3, 0]
print("\nProbando calculate_delta directamente para [0, 3, 0]:")

if 1 in engine.motion_states:
    motion = engine.motion_states[1]
    comp = motion.active_components['manual_macro_rotation']
    
    # Forzar estado
    test_state = motion.state
    test_state.position = np.array([0.0, 3.0, 0.0])
    
    print(f"  Posición de prueba: {test_state.position}")
    print(f"  Centro de rotación: {comp.center}")
    
    # Calcular posición relativa
    relative_pos = test_state.position - comp.center
    print(f"  Posición relativa: {relative_pos}")
    
    # Calcular ángulo actual
    current_angle = np.arctan2(relative_pos[1], relative_pos[0])
    print(f"  Ángulo actual: {current_angle:.3f} rad ({math.degrees(current_angle):.1f}°)")
    
    # El delta
    delta = comp.calculate_delta(test_state, 0.0, 0.016)
    if delta:
        print(f"  Delta: {delta.position}")
        print(f"  ¿Es exactamente [0,0,0]? {np.allclose(delta.position, [0,0,0])}")

print("\n💡 POSIBLE CAUSA:")
print("Si el delta es [0,0,0] para la fuente 1, puede ser porque:")
print("1. El ángulo actual ya es igual al target")
print("2. Hay un caso especial en el algoritmo para Y positivo")
print("3. La interpolación está calculando que no necesita moverse")