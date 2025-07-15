# === test_individual_working.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np

print("🧪 Test de IndividualTrajectory con active_components dict...")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

print("\n📋 Verificando estructura:")
for sid in [0, 1, 2]:
    motion = engine.motion_states[sid]
    print(f"  Fuente {sid}: active_components es {type(motion.active_components)}")

# Configurar trayectorias
shapes = ["circle", "spiral", "figure8"]
for sid, shape in zip([0, 1, 2], shapes):
    motion = engine.motion_states[sid]
    
    # Crear componente
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = shape
    traj.shape_params = {"radius": 1.0 + sid * 0.5}
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = 0.5
    traj.center = np.zeros(3)
    traj.position_on_trajectory = 0.0
    
    # Añadir al diccionario
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ {shape} configurado para fuente {sid}")

# Guardar posiciones iniciales
initial = {}
for sid in [0, 1, 2]:
    initial[sid] = engine._positions[sid].copy()

print("\n🏃 Simulando 2 segundos...")
# Procesar deltas manualmente (hasta que arreglemos engine.update)
for frame in range(120):  # 2 segundos a 60 fps
    dt = 1/60
    
    for sid in [0, 1, 2]:
        motion = engine.motion_states[sid]
        deltas = motion.update_with_deltas(dt)
        
        for delta in deltas:
            if delta.position is not None:
                engine._positions[sid] += delta.position
    
    # Mostrar progreso cada 0.5 segundos
    if frame % 30 == 0 and frame > 0:
        print(f"\n  T = {frame/60:.1f}s:")
        for sid, shape in zip([0, 1, 2], shapes):
            pos = engine._positions[sid]
            dist = np.linalg.norm(pos - initial[sid])
            traj = motion.active_components['individual_trajectory']
            phase = traj.position_on_trajectory
            print(f"    {shape}: dist={dist:.3f}, phase={phase:.3f}")

# Resultados finales
print("\n📊 RESULTADOS FINALES:")
success = True
for sid, shape in zip([0, 1, 2], shapes):
    final_pos = engine._positions[sid]
    dist = np.linalg.norm(final_pos - initial[sid])
    
    if dist > 0.01:
        print(f"  ✅ {shape} (fuente {sid}): Movió {dist:.3f} unidades")
    else:
        print(f"  ❌ {shape} (fuente {sid}): NO se movió")
        success = False

if success:
    print("\n🎉 ¡ÉXITO! IndividualTrajectory migrado a deltas correctamente!")
    print("\n📝 Siguiente: Migrar MacroTrajectory")
    print("   Ejecuta: python migrate_macro_trajectory.py")
else:
    print("\n❌ Debug necesario")
