# === test_trajectory_simple.py ===
from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("🧪 Test simple de trayectorias...")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
engine.create_macro("test", [0, 1, 2])

# Debug: ver qué tenemos
print("\n📋 Estado después de crear macro:")
print(f"  motion_states keys: {list(engine.motion_states.keys())}")
print(f"  Tipo active_components[0]: {type(engine.motion_states[0].active_components)}")

# Intentar crear trayectoria directamente
print("\n🔧 Creando trayectoria manualmente...")
from trajectory_hub.core.motion_components import IndividualTrajectory

for sid in [0, 1, 2]:
    motion = engine.motion_states[sid]
    
    # Crear componente
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = "circle"
    traj.movement_mode = "fix"
    traj.movement_speed = 0.5
    traj.set_trajectory("circle", radius=1.0)
    
    # Añadir al motion
    if isinstance(motion.active_components, dict):
        motion.active_components['individual_trajectory'] = traj
    else:
        # Si es lista, cambiar a dict
        motion.active_components = {'individual_trajectory': traj}
    
    print(f"  ✅ Trayectoria añadida a fuente {sid}")

# Test de movimiento
print("\n🏃 Test de movimiento...")
initial = engine._positions.copy()

# Simular (sin parámetro dt)
for _ in range(60):
    engine.update()

# Verificar
print("\n📊 Resultados:")
for sid in [0, 1, 2]:
    dist = np.linalg.norm(engine._positions[sid] - initial[sid])
    print(f"  Fuente {sid}: movió {dist:.3f}")
    
    # Debug del componente
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        if 'individual_trajectory' in motion.active_components:
            traj = motion.active_components['individual_trajectory']
            print(f"    Phase: {getattr(traj, 'position_on_trajectory', 0):.3f}")
