# === diagnose_individual_update.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import TrajectoryMovementMode

print("🔍 Diagnóstico de IndividualTrajectory con deltas...")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
engine.create_macro("test", [0])

# Configurar trayectoria
engine.configure_individual_trajectories("test", mode=1)

# Obtener componentes
sid = 0
motion = engine.motion_states[sid]
print(f"\n✅ SourceMotion creado para fuente {sid}")
print(f"  Componentes activos: {list(motion.active_components.keys())}")

if 'individual_trajectory' in motion.active_components:
    traj = motion.active_components['individual_trajectory']
    print(f"\n✅ IndividualTrajectory encontrado")
    print(f"  Enabled: {traj.enabled}")
    print(f"  Shape: {getattr(traj, 'shape_type', 'unknown')}")
    print(f"  Movement mode: {getattr(traj, 'movement_mode', 'unknown')}")
    print(f"  Has calculate_delta: {hasattr(traj, 'calculate_delta')}")
    
    # Activar movimiento
    traj.enabled = True
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = 1.0
    
    # Test directo de calculate_delta
    if hasattr(traj, 'calculate_delta'):
        print(f"\n🧪 Test directo de calculate_delta:")
        delta = traj.calculate_delta(motion.state, 0.1)
        print(f"  Delta position: {delta.position}")
        print(f"  Position on trajectory: {traj.position_on_trajectory}")
        
        # Test update_with_deltas
        print(f"\n🧪 Test de update_with_deltas:")
        deltas = motion.update_with_deltas(0.1)
        print(f"  Número de deltas: {len(deltas)}")
        for i, d in enumerate(deltas):
            print(f"  Delta {i}: {d.position}")
else:
    print("❌ No se encontró individual_trajectory en los componentes")
