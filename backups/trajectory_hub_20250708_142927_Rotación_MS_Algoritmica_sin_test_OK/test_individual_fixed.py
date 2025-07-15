# === test_individual_fixed.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np

print("🧪 Test con update_position arreglado...")

# Setup
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

# Configurar manualmente
for sid in [0, 1, 2]:
    motion = engine.motion_states[sid]
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = "circle"
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = 0.5
    traj.set_trajectory("circle", radius=1.0 + sid * 0.5)
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ Trayectoria configurada para fuente {sid}")

# Test directo de update_position
print("\n🧪 Test directo de componente:")
traj = engine.motion_states[0].active_components['individual_trajectory']
print(f"  Phase inicial: {traj.position_on_trajectory}")
traj.update_position(0.1)
print(f"  Phase después de update: {traj.position_on_trajectory}")

# Test de calculate_delta
delta = traj.calculate_delta(engine.motion_states[0].state, 0.1)
print(f"  Delta calculado: {delta.position}")
print(f"  Phase final: {traj.position_on_trajectory}")

# Test completo con engine (necesita el fix del engine también)
print("\n🏃 Simulando con engine...")
initial = engine._positions.copy()

# Si engine.update() no procesa deltas, lo hacemos manualmente por ahora
for i in range(60):
    dt = 1/60
    # Procesar cada motion manualmente
    for sid in [0, 1, 2]:
        motion = engine.motion_states[sid]
        deltas = motion.update_with_deltas(dt)
        for delta in deltas:
            if delta.position is not None:
                engine._positions[sid] += delta.position

# Resultados
print("\n📊 Resultados:")
for sid in [0, 1, 2]:
    dist = np.linalg.norm(engine._positions[sid] - initial[sid])
    status = "✅" if dist > 0.01 else "❌"
    print(f"  Fuente {sid}: {status} Movió {dist:.3f}")

if any(np.linalg.norm(engine._positions[sid] - initial[sid]) > 0.01 for sid in [0, 1, 2]):
    print("\n🎉 ¡Las trayectorias individuales funcionan!")
    print("\n⚠️ Ahora ejecuta: python fix_engine_update_individual.py")
    print("    para que engine.update() procese automáticamente los deltas")
