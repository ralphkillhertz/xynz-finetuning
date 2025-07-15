# === test_delta_minimal.py ===
# Test mínimo del sistema de deltas

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent, MotionDelta
import numpy as np

print("🧪 TEST MÍNIMO DE DELTAS")
print("="*50)

# Test 1: ConcentrationComponent directamente
print("\n1️⃣ Test directo de ConcentrationComponent:")
try:
    comp = ConcentrationComponent()
    comp.enabled = True
    comp.concentration_factor = 0.8
    comp.concentration_center = np.array([0.0, 0.0, 0.0])
    
    # Simular estado
    class FakeState:
        def __init__(self):
            self.position = np.array([10.0, 0.0, 0.0])
            self.source_id = 0
    
    state = FakeState()
    
    # Calcular delta
    if hasattr(comp, 'calculate_delta'):
        delta = comp.calculate_delta(state, 0.0, 0.1)
        if delta:
            print(f"  ✅ Delta calculado: {delta.position}")
        else:
            print("  ❌ Delta es None")
    else:
        print("  ❌ ConcentrationComponent no tiene calculate_delta")
        
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Sistema completo
print("\n2️⃣ Test del sistema completo:")
try:
    engine = EnhancedTrajectoryEngine(max_sources=3)
    engine.running = True
    
    # Crear fuente
    engine.create_source(0, "test")
    print("  ✅ Fuente creada")
    
    # Posición inicial
    engine._positions[0] = np.array([10.0, 0.0, 0.0])
    print(f"  📍 Posición inicial: {engine._positions[0]}")
    
    # Aplicar concentración manualmente
    if 0 in engine.motion_states:
        motion = engine.motion_states[0]
        comp = ConcentrationComponent()
        comp.enabled = True
        comp.concentration_factor = 0.8
        comp.concentration_center = np.array([0.0, 0.0, 0.0])
        
        # Añadir componente
        if hasattr(motion, 'add_component'):
            motion.add_component(comp, 'concentration')
            print("  ✅ Concentración añadida")
        else:
            print("  ⚠️ No se puede añadir componente")
    
    # Ejecutar step
    engine.step()
    print(f"  📍 Posición después de step: {engine._positions[0]}")
    
    # Verificar movimiento
    if not np.array_equal(engine._positions[0], [10.0, 0.0, 0.0]):
        print("  ✅ ¡LA FUENTE SE MOVIÓ!")
    else:
        print("  ❌ La fuente NO se movió")
        
except Exception as e:
    print(f"  ❌ Error: {e}")
    import traceback
    traceback.print_exc()
