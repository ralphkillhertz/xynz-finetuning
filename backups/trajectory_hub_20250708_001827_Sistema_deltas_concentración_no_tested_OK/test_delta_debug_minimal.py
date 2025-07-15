# === test_delta_debug_minimal.py ===
# Test mínimo con debug detallado

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent, MotionDelta
import numpy as np

print("🔍 DEBUG MÍNIMO DEL SISTEMA")
print("="*50)

# Test 1: ConcentrationComponent directamente
print("\n1️⃣ Test directo de ConcentrationComponent:")
comp = ConcentrationComponent()
comp.enabled = True
comp.concentration_factor = 0.8
comp.concentration_center = np.array([0.0, 0.0, 0.0])

# Estado falso
class FakeState:
    def __init__(self):
        self.position = np.array([10.0, 0.0, 0.0])
        self.source_id = 0

state = FakeState()

# Calcular delta
delta = comp.calculate_delta(state, 0.0, 0.1)
print(f"  Delta calculado: {delta}")
if delta:
    print(f"  - position: {delta.position}")
    print(f"  - source_id: {delta.source_id}")

# Test 2: SourceMotion
print("\n2️⃣ Test de SourceMotion.update_with_deltas:")
from trajectory_hub.core.motion_components import SourceMotion, MotionState

motion_state = MotionState()
motion_state.position = np.array([10.0, 0.0, 0.0])
motion_state.source_id = 0

motion = SourceMotion(motion_state)
motion.source_id = 0

# Añadir componente
motion.add_component(comp, 'concentration')

# Llamar update_with_deltas
result = motion.update_with_deltas(0.0, 0.1)
print(f"  Resultado: {result}")
print(f"  - Tipo: {type(result)}")
print(f"  - Es lista: {isinstance(result, list)}")

if isinstance(result, list):
    print(f"  - Longitud: {len(result)}")
    for i, d in enumerate(result):
        print(f"  - Delta {i}: {d}")
        if hasattr(d, 'position'):
            print(f"    position: {d.position}")
else:
    print("  ❌ NO es una lista!")
    if hasattr(result, 'position'):
        print(f"  - position: {result.position}")

# Test 3: Sistema completo
print("\n3️⃣ Test del sistema completo:")
engine = EnhancedTrajectoryEngine(max_sources=1)
engine.running = True
engine.create_source(0, "test")
engine._positions[0] = np.array([10.0, 0.0, 0.0])

# Aplicar concentración
motion = engine.motion_states[0]
motion.add_component(comp, 'concentration')

print(f"  Posición antes: {engine._positions[0]}")

# Un solo step con debug
if hasattr(engine, 'step'):
    engine.step()
else:
    print("  ❌ No existe engine.step()")

print(f"  Posición después: {engine._positions[0]}")
