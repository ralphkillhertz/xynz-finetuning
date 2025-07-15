# === test_individual_quick.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np

print("🧪 Test rápido de IndividualTrajectory...")

# Setup mínimo
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

print("✅ Configurado")

# Test update_with_deltas
print("\n🧪 Probando update_with_deltas...")
try:
    deltas = motion.update_with_deltas(0.1)
    print(f"✅ Funcionó! Deltas: {len(deltas)}")
    if deltas:
        print(f"   Delta[0]: {deltas[0].position}")
except Exception as e:
    print(f"❌ Error: {e}")

# Simulación rápida
print("\n🏃 Simulación rápida (1 segundo)...")
initial = engine._positions[0].copy()

for i in range(60):
    dt = 1/60
    try:
        deltas = motion.update_with_deltas(dt)
        for delta in deltas:
            if delta and delta.position is not None:
                engine._positions[0] += delta.position
    except Exception as e:
        print(f"❌ Error en frame {i}: {e}")
        break

final = engine._positions[0]
distance = np.linalg.norm(final - initial)

print(f"\n📊 Resultado:")
print(f"   Posición inicial: {initial}")
print(f"   Posición final: {final}")
print(f"   Distancia: {distance:.3f}")
print(f"   Phase final: {traj.position_on_trajectory:.3f}")

if distance > 0.1:
    print("\n✅ ¡IndividualTrajectory funciona con deltas!")
    print("\n📝 Próximos pasos:")
    print("   1. Arreglar engine.update() para procesar deltas automáticamente")
    print("   2. Migrar MacroTrajectory a deltas")
    print("   3. Migrar rotaciones a deltas")
else:
    print("\n❌ No hubo movimiento suficiente")
