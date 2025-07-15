# === debug_concentration_logic.py ===
# 🔧 Debug de la lógica de concentración
# ⚡ Por qué el delta es [0,0,0]

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent

print("🔍 DEBUG DE LÓGICA DE CONCENTRACIÓN")
print("="*60)

# Setup simple
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=1)
engine._positions[0] = np.array([10.0, 0.0, 0.0])

print(f"📍 Posición inicial: {engine._positions[0]}")

# Aplicar concentración
engine.set_macro_concentration(macro, factor=0.5)

# Obtener componente
motion = engine.motion_states[0]
comp = motion.active_components[0]

print(f"\n🔍 ConcentrationComponent:")
print(f"   enabled: {comp.enabled}")
print(f"   factor: {comp.concentration_factor}")
print(f"   center: {comp.center}")
print(f"   target_point: {getattr(comp, 'target_point', 'NO EXISTE')}")
print(f"   macro_center: {getattr(comp, 'macro_center', 'NO EXISTE')}")

# Debug del state
state = motion.state
print(f"\n🔍 MotionState:")
print(f"   position: {state.position}")
print(f"   source_id: {state.source_id}")

# Cálculo manual
print(f"\n🧮 Cálculo manual del delta:")
position = state.position
center = comp.center
print(f"   position: {position}")
print(f"   center: {center}")

# Verificar si position y center son iguales
if np.array_equal(position, center):
    print("   ⚠️ ¡Position y center son IGUALES!")
    print("   Por eso el delta es [0,0,0]")
else:
    direction = center - position
    print(f"   direction (center - position): {direction}")
    movement = direction * comp.concentration_factor * 0.016
    print(f"   movement esperado: {movement}")

# Test con diferentes valores
print(f"\n🧪 Test con state.position corregido:")
# Forzar la posición correcta
state.position = engine._positions[0].copy()
print(f"   state.position (corregido): {state.position}")

delta = comp.calculate_delta(state, 0, 0.016)
print(f"   Delta calculado: {delta}")
if hasattr(delta, 'position'):
    print(f"   Delta.position: {delta.position}")

# Verificar si el problema es que state.position no se actualiza
print(f"\n🔍 ¿Se actualiza state.position?")
print(f"   engine._positions[0]: {engine._positions[0]}")
print(f"   motion.state.position: {motion.state.position}")
print(f"   Son iguales: {np.array_equal(engine._positions[0], motion.state.position)}")

if not np.array_equal(engine._positions[0], motion.state.position):
    print("\n❌ PROBLEMA: state.position no refleja engine._positions")
    print("   Esto causa que el delta sea 0")