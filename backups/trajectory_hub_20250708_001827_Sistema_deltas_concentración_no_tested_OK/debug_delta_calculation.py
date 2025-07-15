# === debug_delta_calculation.py ===
# 🔧 Debug profundo del cálculo de deltas
# ⚡ Qué está pasando EXACTAMENTE

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🔍 DEBUG PROFUNDO DE CÁLCULO DE DELTAS")
print("="*60)

# Setup mínimo
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=1)
engine._positions[0] = np.array([10.0, 0.0, 0.0])

print(f"📍 Posición inicial: {engine._positions[0]}")

# Aplicar concentración
engine.set_macro_concentration(macro, factor=0.8)

# Debug paso a paso
motion = engine.motion_states[0]
comp = motion.active_components[0]

print(f"\n🔍 ConcentrationComponent:")
print(f"   concentration_factor: {comp.concentration_factor}")
print(f"   target_point: {comp.target_point}")
print(f"   macro_center: {comp.macro_center}")

print(f"\n🔍 MotionState ANTES de update:")
print(f"   state.position: {motion.state.position}")

# Simular lo que hace engine.update()
print(f"\n🔄 Simulando engine.update():")

# 1. Sincronizar posición
motion.state.position = engine._positions[0].copy()
print(f"   ✅ Sincronizado: state.position = {motion.state.position}")

# 2. Calcular delta manualmente
print(f"\n🧮 Cálculo manual del delta:")
current_pos = motion.state.position
target = comp.target_point
print(f"   current_pos: {current_pos}")
print(f"   target: {target}")

direction = target - current_pos
print(f"   direction (target - current): {direction}")
distance = np.linalg.norm(direction)
print(f"   distance: {distance}")

if distance > 0:
    movement = direction * comp.concentration_factor * 0.016
    print(f"   movement (direction * factor * dt): {movement}")
else:
    print("   ❌ Distance es 0, no hay movimiento")

# 3. Llamar calculate_delta real
print(f"\n🧪 calculate_delta real:")
delta = comp.calculate_delta(motion.state, 0, 0.016)
print(f"   Delta: {delta}")
if hasattr(delta, 'position'):
    print(f"   Delta.position: {delta.position}")

# 4. Verificar el código de calculate_delta
print(f"\n🔍 Verificando lógica de calculate_delta:")
print(f"   ¿target_point es correcto? {comp.target_point}")
print(f"   ¿Es igual a la posición actual? {np.array_equal(comp.target_point, current_pos)}")

# 5. Solución si target_point es incorrecto
if np.array_equal(comp.target_point, [0, 0, 0]) and comp.macro_center != [0, 0, 0]:
    print(f"\n⚠️ PROBLEMA: target_point es [0,0,0] pero macro_center es {comp.macro_center}")
    print("   ConcentrationComponent está usando el target incorrecto")
    
    # Test con target correcto
    print(f"\n🔧 Test con target_point = macro_center:")
    comp.target_point = comp.macro_center
    delta2 = comp.calculate_delta(motion.state, 0, 0.016)
    if hasattr(delta2, 'position'):
        print(f"   Nuevo delta.position: {delta2.position}")