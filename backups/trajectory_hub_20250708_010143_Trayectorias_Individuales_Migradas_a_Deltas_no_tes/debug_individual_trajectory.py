# === debug_individual_trajectory.py ===
# 🔧 Fix: Debug detallado para ver dónde falla
# ⚡ Test paso a paso con más información

from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np

print("🔍 Debug detallado de IndividualTrajectory...\n")

# Crear engine con solo 1 fuente
engine = EnhancedTrajectoryEngine(max_sources=1, fps=60)
engine.create_macro("test", [0])

motion = engine.motion_states[0]
print(f"✅ Motion state creado")
print(f"   active_components tipo: {type(motion.active_components)}")

# Crear trayectoria simple (solo círculo)
traj = IndividualTrajectory()
traj.enabled = True
traj.shape_type = "circle"
traj.shape_params = {"radius": 2.0}
traj.movement_mode = TrajectoryMovementMode.FIX
traj.movement_speed = 1.0
traj.center = np.zeros(3)
traj.position_on_trajectory = 0.0

motion.active_components['individual_trajectory'] = traj
print(f"✅ Trayectoria añadida")

# Test 1: update_position
print("\n🧪 Test 1: update_position")
try:
    print(f"   Phase antes: {traj.position_on_trajectory}")
    traj.update_position(0.1)
    print(f"   Phase después: {traj.position_on_trajectory}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: _calculate_position_on_trajectory
print("\n🧪 Test 2: _calculate_position_on_trajectory")
try:
    pos = traj._calculate_position_on_trajectory(0.0)
    print(f"   Posición en fase 0.0: {pos}")
    pos = traj._calculate_position_on_trajectory(0.25)
    print(f"   Posición en fase 0.25: {pos}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: calculate_delta
print("\n🧪 Test 3: calculate_delta")
try:
    delta = traj.calculate_delta(motion.state, 0.1)
    print(f"   Delta position: {delta.position}")
    print(f"   Delta es None?: {delta.position is None}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: update_with_deltas
print("\n🧪 Test 4: update_with_deltas")
try:
    deltas = motion.update_with_deltas(0.1)
    print(f"   Deltas retornados: {len(deltas)}")
    for i, d in enumerate(deltas):
        print(f"   Delta {i}: {d.position}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Simulación corta
print("\n🧪 Test 5: Simulación corta (10 frames)")
initial = engine._positions[0].copy()
print(f"   Posición inicial: {initial}")

try:
    for i in range(10):
        dt = 1/60
        deltas = motion.update_with_deltas(dt)
        
        print(f"\n   Frame {i}:")
        print(f"     Phase: {traj.position_on_trajectory:.3f}")
        print(f"     Deltas: {len(deltas)}")
        
        for delta in deltas:
            if delta and delta.position is not None:
                print(f"     Delta: {delta.position}")
                engine._positions[0] += delta.position
            else:
                print(f"     Delta vacío o None")
        
        print(f"     Posición: {engine._positions[0]}")
        
except Exception as e:
    print(f"   ❌ Error en frame {i}: {e}")
    import traceback
    traceback.print_exc()

# Resultado final
final = engine._positions[0]
dist = np.linalg.norm(final - initial)
print(f"\n📊 Resultado:")
print(f"   Distancia total: {dist:.3f}")
print(f"   Posición final: {final}")

if dist > 0.001:
    print("\n✅ La trayectoria se está moviendo!")
else:
    print("\n❌ No hay movimiento")