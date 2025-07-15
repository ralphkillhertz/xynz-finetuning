# === debug_engine_update.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np

print("🔍 Debug de engine.update()...")

engine = EnhancedTrajectoryEngine(max_sources=1, fps=60)
engine.create_macro("test", [0])

motion = engine.motion_states[0]
traj = IndividualTrajectory()
traj.enabled = True
traj.shape_type = "circle"
traj.shape_params = {"radius": 2.0}
traj.movement_mode = TrajectoryMovementMode.FIX
traj.movement_speed = 1.0
traj.center = np.zeros(3)
motion.active_components['individual_trajectory'] = traj

print("✅ Configuración completa")
print(f"  Posición inicial: {engine._positions[0]}")

# Test un solo update
try:
    engine.update()
    print(f"  Posición después de update: {engine._positions[0]}")
    print("✅ engine.update() funciona!")
except Exception as e:
    print(f"❌ Error en update: {e}")
    import traceback
    traceback.print_exc()
