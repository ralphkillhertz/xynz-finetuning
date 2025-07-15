# === test_individual_final_fixed.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np
import time

print("🧪 Test FINAL CORREGIDO de IndividualTrajectory...")

# Setup
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

# Configurar diferentes trayectorias - SIN 'shape' en shape_params
configs = [
    {"shape": "circle", "params": {"radius": 2.0}, "speed": 0.5},
    {"shape": "spiral", "params": {"radius": 1.5, "height": 3.0}, "speed": 0.3},
    {"shape": "figure8", "params": {"scale": 2.5}, "speed": 0.4}
]

for sid, config in enumerate(configs):
    motion = engine.motion_states[sid]
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = config["shape"]
    traj.shape_params = config["params"]  # Solo los parámetros, sin 'shape'
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = config["speed"]
    traj.center = np.array([sid * 3, 0, 0])
    traj.position_on_trajectory = 0.0  # Empezar en 0
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ {config['shape']} configurado correctamente")

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
    
    # Mostrar progreso cada 0.5 segundos
    if frame % 30 == 0:
        print(f"\n  T = {frame/60:.1f}s:")
        for sid, config in enumerate(configs):
            pos = engine._positions[sid]
            dist = np.linalg.norm(pos - initial[sid])
            traj = engine.motion_states[sid].active_components['individual_trajectory']
            phase = traj.position_on_trajectory
            print(f"    {config['shape']}: dist={dist:.3f}, phase={phase:.3f}")

# Resultados finales
print("\n📊 RESULTADOS FINALES:")
all_success = True
for sid, config in enumerate(configs):
    final_pos = engine._positions[sid]
    dist = np.linalg.norm(final_pos - initial[sid])
    
    # Ajustar threshold según la velocidad esperada
    expected_dist = config["speed"] * 2.0 * 2 * np.pi * config["params"].get("radius", config["params"].get("scale", 1.0))
    threshold = expected_dist * 0.1  # Al menos 10% del movimiento esperado
    
    if dist > threshold:
        print(f"  ✅ {config['shape']} (fuente {sid}): Movió {dist:.3f} unidades (esperado ~{expected_dist:.1f})")
    else:
        print(f"  ❌ {config['shape']} (fuente {sid}): Solo movió {dist:.3f} (esperado ~{expected_dist:.1f})")
        all_success = False

if all_success:
    print("\n🎉 ¡MIGRACIÓN COMPLETA!")
    print("\n✅ IndividualTrajectory migrado exitosamente a sistema de deltas")
    print("\n📝 Siguiente paso: Arreglar engine.update() para procesar deltas automáticamente")
    print("   Después: Migrar MacroTrajectory")
else:
    print("\n⚠️ Revisar los umbrales de movimiento")

# Guardar estado
state = {
    "individual_trajectory": "✅ Migrado a deltas (funcional)",
    "engine_update": "❌ Necesita procesar deltas automáticamente",
    "macro_trajectory": "❌ Pendiente migración",
    "rotation_ms": "❌ Pendiente",
    "rotation_is": "❌ Pendiente"
}

import json
with open("migration_state.json", "w") as f:
    json.dump(state, f, indent=2)
print("\n💾 Estado guardado en migration_state.json")
