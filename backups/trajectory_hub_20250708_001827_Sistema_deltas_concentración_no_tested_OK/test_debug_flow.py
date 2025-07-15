# === test_debug_flow.py ===
# Test con debug detallado del flujo

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent
import numpy as np

print("🔍 TEST DEBUG DETALLADO")
print("="*50)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=3)
engine.running = True

# Verificar métodos disponibles
print("\n📋 Métodos disponibles en engine:")
methods = [m for m in dir(engine) if not m.startswith('_') and callable(getattr(engine, m))]
update_methods = [m for m in methods if any(k in m.lower() for k in ['update', 'step', 'tick', 'run'])]
print(f"  Métodos de actualización: {update_methods}")

# Crear fuente
engine.create_source(0, "test")
engine._positions[0] = np.array([10.0, 0.0, 0.0])

# Añadir concentración
motion = engine.motion_states[0]
comp = ConcentrationComponent()
comp.enabled = True
comp.concentration_factor = 0.8
comp.concentration_center = np.array([0.0, 0.0, 0.0])
motion.add_component(comp, 'concentration')

print(f"\n📍 Posición inicial: {engine._positions[0]}")

# Probar diferentes métodos
for method_name in ['step', 'update', 'tick', 'run']:
    if hasattr(engine, method_name):
        print(f"\n🔄 Llamando engine.{method_name}()...")
        method = getattr(engine, method_name)
        try:
            method()
            print(f"  ✅ {method_name}() ejecutado")
            print(f"  📍 Posición después: {engine._positions[0]}")
            
            if not np.array_equal(engine._positions[0], [10.0, 0.0, 0.0]):
                print(f"  🎯 ¡FUNCIONA con {method_name}()!")
                break
        except Exception as e:
            print(f"  ❌ Error: {e}")
    else:
        print(f"\n❌ No existe engine.{method_name}()")
