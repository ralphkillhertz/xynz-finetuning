# === test_individual_deltas_fixed.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import time

print("🧪 Test de IndividualTrajectory con sistema de deltas...")

# Crear engine con argumentos correctos
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Crear macro con 3 fuentes
engine.create_macro("test", [0, 1, 2])

# Configurar trayectorias individuales
print("\nConfigurando trayectorias individuales...")
engine.configure_individual_trajectories("test", mode=1)  # Modo 1: todas círculos

# Verificar que se crearon
for sid in [0, 1, 2]:
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        if 'individual_trajectory' in motion.active_components:
            traj = motion.active_components['individual_trajectory']
            traj.enabled = True
            traj.movement_mode = 'fix'  # O usar TrajectoryMovementMode.FIX si está importado
            traj.movement_speed = 0.5
            print(f"  ✅ Fuente {sid}: trayectoria configurada")

print("\nPosiciones iniciales:")
for sid in [0, 1, 2]:
    pos = engine._positions[sid]
    print(f"  Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

# Simular 2 segundos
print("\nSimulando movimiento...")
for i in range(120):  # 2 segundos a 60 fps
    engine.update(1/60)
    
    if i % 30 == 0:  # Cada 0.5 segundos
        print(f"\nT={i/60:.1f}s:")
        for sid in [0, 1, 2]:
            pos = engine._positions[sid]
            print(f"  Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
            
            # Debug: verificar estado del componente
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                if 'individual_trajectory' in motion.active_components:
                    traj = motion.active_components['individual_trajectory']
                    print(f"    Phase: {getattr(traj, 'position_on_trajectory', 0):.2f}")

print("\n✅ Test completado!")

# Verificar si hubo movimiento
moved = False
for sid in [0, 1, 2]:
    initial = engine._initial_positions[sid] if hasattr(engine, '_initial_positions') else np.zeros(3)
    final = engine._positions[sid]
    if np.linalg.norm(final - initial) > 0.1:
        moved = True
        break

if moved:
    print("✅ ¡Las trayectorias individuales funcionan con deltas!")
else:
    print("❌ Las fuentes no se movieron. Verificar implementación.")
