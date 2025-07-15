# === diagnose_circle_issue.py ===
# 🔧 Fix: Diagnosticar por qué circle no funciona
# ⚡ Pero spiral y figure8 sí

from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np
import time

print("🔍 Diagnóstico específico de circle vs spiral...")

# Setup
engine = EnhancedTrajectoryEngine(max_sources=2, fps=60)
engine.create_macro("test", [0, 1])

# Configurar circle y spiral
configs = [
    {"shape": "circle", "radius": 2.0},
    {"shape": "spiral", "radius": 1.5, "height": 3.0}
]

for sid, config in enumerate(configs):
    motion = engine.motion_states[sid]
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = config["shape"]
    traj.shape_params = config
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = 0.5
    traj.center = np.zeros(3)
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ {config['shape']} configurado")

# Test _calculate_position_on_trajectory
print("\n🧪 Test de _calculate_position_on_trajectory:")
for sid, config in enumerate(configs):
    traj = engine.motion_states[sid].active_components['individual_trajectory']
    print(f"\n{config['shape']}:")
    
    # Probar diferentes fases
    for phase in [0.0, 0.25, 0.5]:
        pos = traj._calculate_position_on_trajectory(phase)
        print(f"  Phase {phase}: {pos}")

# Test calculate_delta
print("\n🧪 Test de calculate_delta:")
for sid, config in enumerate(configs):
    motion = engine.motion_states[sid]
    traj = motion.active_components['individual_trajectory']
    
    print(f"\n{config['shape']}:")
    print(f"  Phase inicial: {traj.position_on_trajectory}")
    
    # Calcular delta
    delta = traj.calculate_delta(motion.state, 0.1)
    print(f"  Delta: {delta.position}")
    print(f"  Phase después: {traj.position_on_trajectory}")
    
    # Ver si el estado tiene la posición guardada
    if hasattr(motion.state, 'individual_trajectory_position'):
        print(f"  State position: {motion.state.individual_trajectory_position}")

# Test update_with_deltas
print("\n🧪 Test de update_with_deltas:")
current_time = time.time()
for sid, config in enumerate(configs):
    motion = engine.motion_states[sid]
    deltas = motion.update_with_deltas(current_time, 0.1)
    print(f"\n{config['shape']}: {len(deltas)} deltas")
    for i, delta in enumerate(deltas):
        print(f"  Delta {i}: {delta.position}")

# Simular unos frames manualmente
print("\n🏃 Simulación manual corta:")
initial = [engine._positions[i].copy() for i in range(2)]

for frame in range(5):
    print(f"\nFrame {frame}:")
    current_time = time.time() + frame/60
    
    for sid, config in enumerate(configs):
        motion = engine.motion_states[sid]
        traj = motion.active_components['individual_trajectory']
        
        # Estado antes
        old_pos = engine._positions[sid].copy()
        old_phase = traj.position_on_trajectory
        
        # Aplicar deltas
        deltas = motion.update_with_deltas(current_time, 1/60)
        for delta in deltas:
            if delta.position is not None:
                engine._positions[sid] += delta.position
        
        # Estado después
        new_pos = engine._positions[sid]
        new_phase = traj.position_on_trajectory
        moved = np.linalg.norm(new_pos - old_pos)
        
        print(f"  {config['shape']}: phase {old_phase:.3f}→{new_phase:.3f}, movió {moved:.3f}")

# Resultado final
print("\n📊 Resultado después de 5 frames:")
for sid, config in enumerate(configs):
    dist = np.linalg.norm(engine._positions[sid] - initial[sid])
    print(f"  {config['shape']}: distancia total = {dist:.3f}")

# Verificar si es problema con shape_params
print("\n🔍 Verificando shape_params:")
for sid, config in enumerate(configs):
    traj = engine.motion_states[sid].active_components['individual_trajectory']
    print(f"  {config['shape']}: shape_params = {traj.shape_params}")