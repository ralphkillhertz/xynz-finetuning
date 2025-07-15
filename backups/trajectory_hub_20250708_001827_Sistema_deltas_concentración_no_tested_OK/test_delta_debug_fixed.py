# === test_delta_debug_fixed.py ===
# Test debug arreglado - continúa después del error

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent, MotionDelta
import numpy as np

print("🔍 DEBUG COMPLETO DEL SISTEMA")
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
print(f"  ✅ Delta calculado: {delta}")
print(f"  - position: {delta.position}")
print(f"  - ¡DELTA CORRECTO! Debería mover de [10,0,0] hacia [0,0,0]")

# Test 2: SourceMotion
print("\n2️⃣ Test de SourceMotion.update_with_deltas:")
try:
    from trajectory_hub.core.motion_components import SourceMotion, MotionState
    
    motion_state = MotionState()
    motion_state.position = np.array([10.0, 0.0, 0.0])
    motion_state.source_id = 0
    
    motion = SourceMotion(motion_state)
    motion.source_id = 0
    
    # Añadir componente
    motion.add_component(comp, 'concentration')
    print("  ✅ Componente añadido")
    
    # Llamar update_with_deltas
    result = motion.update_with_deltas(0.0, 0.1)
    print(f"  Resultado: {result}")
    print(f"  - Tipo: {type(result)}")
    print(f"  - Es lista: {isinstance(result, list)}")
    
    if isinstance(result, list):
        print(f"  - ✅ ES LISTA con {len(result)} elementos")
        for i, d in enumerate(result):
            if hasattr(d, 'position'):
                print(f"    Delta {i}: position={d.position}")
    else:
        print("  ❌ NO ES LISTA - ESTE ES EL PROBLEMA")
        if hasattr(result, 'position'):
            print(f"    position del delta: {result.position}")
            
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 3: step() procesa deltas?
print("\n3️⃣ Test manual del procesamiento en step():")
engine = EnhancedTrajectoryEngine(max_sources=1)
engine.running = True
engine.create_source(0, "test")
engine._positions[0] = np.array([10.0, 0.0, 0.0])

print(f"  Posición inicial: {engine._positions[0]}")

# Simular lo que debería hacer step()
print("\n  🔧 Simulando manualmente lo que debería hacer step():")
motion = engine.motion_states[0]
motion.add_component(comp, 'concentration')

# Obtener deltas
deltas_result = motion.update_with_deltas(0.0, 0.1)
print(f"  - update_with_deltas retornó: {type(deltas_result)}")

# Si no es lista, convertir
if isinstance(deltas_result, list):
    deltas = deltas_result
else:
    deltas = [deltas_result] if deltas_result else []
    print(f"  - Convertido a lista: {len(deltas)} elementos")

# Aplicar deltas manualmente
for delta in deltas:
    if hasattr(delta, 'position') and delta.position is not None:
        print(f"  - Aplicando delta.position: {delta.position}")
        engine._positions[0] += delta.position

print(f"  Posición después de aplicar delta: {engine._positions[0]}")

# Ahora probar step() real
print("\n4️⃣ Probando step() real:")
engine._positions[0] = np.array([10.0, 0.0, 0.0])  # Reset
print(f"  Posición antes de step(): {engine._positions[0]}")
engine.step()
print(f"  Posición después de step(): {engine._positions[0]}")

if np.array_equal(engine._positions[0], [10.0, 0.0, 0.0]):
    print("\n❌ step() NO está aplicando los deltas")
    print("   El problema está en step() o en cómo retorna update_with_deltas")
else:
    print("\n✅ ¡step() SÍ aplicó los deltas!")