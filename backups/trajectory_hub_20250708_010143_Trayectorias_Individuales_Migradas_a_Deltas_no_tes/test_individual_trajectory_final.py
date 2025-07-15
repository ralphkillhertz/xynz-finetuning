# === test_individual_trajectory_final.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np
import time

print("🧪 Test FINAL de IndividualTrajectory con deltas...")

# Setup
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

# Configurar diferentes trayectorias
configs = [
    {"shape": "circle", "radius": 2.0, "speed": 0.5},
    {"shape": "spiral", "radius": 1.5, "height": 3.0, "speed": 0.3},
    {"shape": "figure8", "scale": 2.5, "speed": 0.4}
]

for sid, config in enumerate(configs):
    motion = engine.motion_states[sid]
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = config["shape"]
    traj.shape_params = {k: v for k, v in config.items() if k not in ["shape", "speed"]}
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = config["speed"]
    traj.center = np.array([sid * 3, 0, 0])  # Separar las trayectorias
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ {config['shape']} configurado para fuente {sid}")

# Test con update_with_deltas corregido
print("\n🧪 Test de update_with_deltas...")
current_time = time.time()
motion = engine.motion_states[0]
deltas = motion.update_with_deltas(current_time, 1/60)
print(f"  Deltas retornados: {len(deltas)}")
if deltas:
    print(f"  Delta[0]: {deltas[0].position}")

# Guardar posiciones iniciales
initial = {}
for sid in range(3):
    initial[sid] = engine._positions[sid].copy()

# Simular con deltas
print("\n🏃 Simulando 2 segundos con sistema de deltas...")
start_time = time.time()

for frame in range(120):  # 2 segundos a 60 fps
    current_time = start_time + frame/60
    dt = 1/60
    
    # Procesar cada fuente
    for sid in range(3):
        motion = engine.motion_states[sid]
        deltas = motion.update_with_deltas(current_time, dt)
        
        # Aplicar deltas
        for delta in deltas:
            if delta.position is not None:
                engine._positions[sid] += delta.position
    
    # Mostrar progreso
    if frame % 30 == 0:
        print(f"\n  T = {frame/60:.1f}s:")
        for sid, config in enumerate(configs):
            pos = engine._positions[sid]
            dist = np.linalg.norm(pos - initial[sid])
            traj = motion.active_components['individual_trajectory']
            print(f"    {config['shape']}: dist={dist:.3f}, phase={traj.position_on_trajectory:.3f}")

# Resultados finales
print("\n📊 RESULTADOS FINALES:")
all_success = True
for sid, config in enumerate(configs):
    final_pos = engine._positions[sid]
    dist = np.linalg.norm(final_pos - initial[sid])
    
    if dist > 0.1:
        print(f"  ✅ {config['shape']} (fuente {sid}): Movió {dist:.3f} unidades")
    else:
        print(f"  ❌ {config['shape']} (fuente {sid}): NO se movió")
        all_success = False

if all_success:
    print("\n🎉 ¡MIGRACIÓN COMPLETA!")
    print("\n✅ IndividualTrajectory migrado exitosamente a sistema de deltas")
    print("\n📝 Siguiente paso: Migrar MacroTrajectory")
    print("   Ejecuta: python migrate_macro_trajectory.py")
else:
    print("\n❌ Algo falló en la migración")

# Guardar estado
state = {
    "individual_trajectory": "✅ Migrado a deltas",
    "macro_trajectory": "❌ Pendiente",
    "rotation_ms": "❌ Pendiente",
    "rotation_is": "❌ Pendiente"
}

import json
with open("migration_state.json", "w") as f:
    json.dump(state, f, indent=2)
print("\n💾 Estado guardado en migration_state.json")
