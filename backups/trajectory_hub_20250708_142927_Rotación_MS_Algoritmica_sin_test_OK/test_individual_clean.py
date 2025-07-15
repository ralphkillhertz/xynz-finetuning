# === test_individual_clean.py ===
from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("🧪 Test limpio de IndividualTrajectory...")

engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0])

# Configurar manualmente
motion = engine.motion_states[0]
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode

traj = IndividualTrajectory()
traj.enabled = True
traj.shape_type = "circle"
traj.shape_params = {"radius": 2.0}
traj.movement_mode = TrajectoryMovementMode.FIX
traj.movement_speed = 1.0
traj.center = np.zeros(3)
motion.active_components['individual_trajectory'] = traj

print("✅ Trayectoria configurada")

# Test calculate_delta
initial_pos = engine._positions[0].copy()
print(f"Posición inicial: {initial_pos}")

# Simular manualmente
for i in range(60):
    deltas = motion.update_with_deltas(1/60)
    for delta in deltas:
        if delta.position is not None:
            engine._positions[0] += delta.position

final_pos = engine._positions[0]
distance = np.linalg.norm(final_pos - initial_pos)

print(f"Posición final: {final_pos}")
print(f"Distancia recorrida: {distance:.3f}")

if distance > 0.1:
    print("\n✅ ¡IndividualTrajectory funciona con deltas!")
else:
    print("\n❌ No hubo movimiento")
