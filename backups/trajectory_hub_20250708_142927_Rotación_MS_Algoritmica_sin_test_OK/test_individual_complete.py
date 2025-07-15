# === test_individual_complete.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np

print("🧪 Test COMPLETO de IndividualTrajectory con deltas...")

# Setup
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

# Configurar manualmente con diferentes formas
shapes = ["circle", "spiral", "figure8"]
for i, (sid, shape) in enumerate(zip([0, 1, 2], shapes)):
    motion = engine.motion_states[sid]
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = shape
    traj.shape_params = {"radius": 1.0 + i*0.5, "scale": 1.0}
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = 0.5
    traj.center = np.array([0., 0., 0.])  # Centro en origen
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ {shape} configurado para fuente {sid}")

# Test directo del componente
print("\n🔬 Test directo del componente:")
traj = engine.motion_states[0].active_components['individual_trajectory']
print(f"  Phase inicial: {traj.position_on_trajectory:.3f}")

# Test _calculate_position_on_trajectory
pos = traj._calculate_position_on_trajectory(0.25)  # 1/4 del círculo
print(f"  Posición en fase 0.25: {pos}")

# Test calculate_delta
delta = traj.calculate_delta(engine.motion_states[0].state, 0.1)
print(f"  Delta calculado: {delta.position}")
print(f"  Phase después: {traj.position_on_trajectory:.3f}")

# Guardar posiciones iniciales
initial = {}
for sid in [0, 1, 2]:
    initial[sid] = engine._positions[sid].copy()

# IMPORTANTE: Actualizar engine para que procese deltas
print("\n🏃 Simulando movimiento...")
print("  (Procesando deltas manualmente por ahora)")

for frame in range(120):  # 2 segundos
    dt = 1/60
    
    # Procesar deltas manualmente
    for sid in [0, 1, 2]:
        motion = engine.motion_states[sid]
        deltas = motion.update_with_deltas(dt)
        
        # Aplicar deltas
        for delta in deltas:
            if delta.position is not None:
                engine._positions[sid] += delta.position
    
    # Mostrar progreso
    if frame % 30 == 0:
        print(f"\n  T = {frame/60:.1f}s:")
        for sid, shape in zip([0, 1, 2], shapes):
            pos = engine._positions[sid]
            dist = np.linalg.norm(pos - initial[sid])
            print(f"    {shape}: pos={pos}, dist={dist:.3f}")

# Resultados finales
print("\n📊 RESULTADOS FINALES:")
all_moved = True
for sid, shape in zip([0, 1, 2], shapes):
    final_pos = engine._positions[sid]
    dist = np.linalg.norm(final_pos - initial[sid])
    
    if dist > 0.01:
        print(f"  ✅ {shape} (fuente {sid}): Se movió {dist:.3f} unidades")
    else:
        print(f"  ❌ {shape} (fuente {sid}): NO se movió")
        all_moved = False

if all_moved:
    print("\n🎉 ¡ÉXITO TOTAL! IndividualTrajectory funciona con deltas!")
    print("\n⚠️ Siguiente paso: python fix_engine_update_individual.py")
    print("   Para que engine.update() procese automáticamente los deltas")
else:
    print("\n❌ Algunas trayectorias no funcionaron")
