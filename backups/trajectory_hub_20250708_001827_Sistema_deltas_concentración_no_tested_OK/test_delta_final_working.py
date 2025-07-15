# === test_delta_final_working.py ===
# Test final corregido

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent
import numpy as np

print("🚀 TEST FINAL DEL SISTEMA DE DELTAS")
print("="*50)

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5)
engine.running = True

# Crear fuentes
print("\n1️⃣ Creando fuentes...")
for i in range(3):
    engine.create_source(i, f"test_{i}")
    print(f"  ✅ Fuente {i} creada")

# Establecer posiciones iniciales
positions_list = [
    np.array([10.0, 0.0, 0.0]),
    np.array([0.0, 10.0, 0.0]),
    np.array([-10.0, 0.0, 0.0])
]

for i, pos in enumerate(positions_list):
    engine._positions[i] = pos.copy()

print("\n📍 Posiciones iniciales:")
for i in range(3):
    print(f"  Source {i}: {engine._positions[i]}")

# Aplicar concentración
print("\n2️⃣ Aplicando concentración...")
for i in range(3):
    if i in engine.motion_states:
        motion = engine.motion_states[i]
        comp = ConcentrationComponent()
        comp.enabled = True
        comp.concentration_factor = 0.8
        comp.concentration_center = np.array([0.0, 0.0, 0.0])
        motion.add_component(comp, 'concentration')
        print(f"  ✅ Concentración aplicada a fuente {i}")

# Simular frames
print("\n3️⃣ Simulando 10 frames...")
for frame in range(10):
    engine.step()
    if frame == 0:
        print(f"  Frame {frame}: {engine._positions[0]}")

print("\n📍 Posiciones finales:")
for i in range(3):
    print(f"  Source {i}: {engine._positions[i]}")

# Verificar movimiento
moved = False
for i in range(3):
    if not np.array_equal(engine._positions[i], positions_list[i]):
        moved = True
        break

if moved:
    print("\n✅ ¡ÉXITO! ¡LAS FUENTES SE MOVIERON!")
    print("🎉 EL SISTEMA DE DELTAS FUNCIONA")
else:
    print("\n❌ Las fuentes NO se movieron")
