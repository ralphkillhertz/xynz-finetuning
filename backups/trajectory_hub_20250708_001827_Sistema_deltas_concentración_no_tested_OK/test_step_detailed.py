# === test_step_detailed.py ===
# Test con máximo debug

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent, SourceMotion
import numpy as np

print("🔍 TEST DETALLADO DE STEP")
print("="*50)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=3)
engine.running = True

# Crear fuente
engine.create_source(0, "test")
engine._positions[0] = np.array([10.0, 0.0, 0.0])

# Verificar motion_states
print(f"\n📋 motion_states: {list(engine.motion_states.keys())}")
motion = engine.motion_states[0]
print(f"  - Tipo de motion: {type(motion).__name__}")
print(f"  - Tiene update_with_deltas: {hasattr(motion, 'update_with_deltas')}")

# Añadir concentración
comp = ConcentrationComponent()
comp.enabled = True
comp.concentration_factor = 0.8
comp.concentration_center = np.array([0.0, 0.0, 0.0])

if hasattr(motion, 'add_component'):
    motion.add_component(comp, 'concentration')
    print("  ✅ Concentración añadida con add_component")
elif hasattr(motion, 'components'):
    motion.components['concentration'] = comp
    print("  ✅ Concentración añadida a components dict")
else:
    print("  ❌ No se puede añadir concentración")

# Test manual de update_with_deltas
print("\n🧪 Test manual de update_with_deltas:")
if hasattr(motion, 'update_with_deltas'):
    deltas = motion.update_with_deltas(0.0, 0.1)
    print(f"  - Deltas retornados: {deltas}")
    if deltas:
        for delta in deltas:
            print(f"    Delta: source_id={delta.source_id}, position={delta.position}")

# Ahora step()
print(f"\n📍 Posición antes de step: {engine._positions[0]}")
engine.step()
print(f"📍 Posición después de step: {engine._positions[0]}")

# Si no se movió, aplicar delta manualmente
if np.array_equal(engine._positions[0], [10.0, 0.0, 0.0]):
    print("\n🔧 Aplicando delta manualmente:")
    if deltas and len(deltas) > 0:
        delta = deltas[0]
        engine._positions[0] += delta.position
        print(f"  ✅ Nueva posición: {engine._positions[0]}")
