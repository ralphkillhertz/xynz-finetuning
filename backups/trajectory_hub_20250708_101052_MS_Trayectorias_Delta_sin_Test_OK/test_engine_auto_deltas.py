# === test_engine_auto_deltas.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np

print("🧪 Test de procesamiento AUTOMÁTICO de deltas en engine.update()...")

# Setup
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

# Configurar trayectorias
shapes = ["circle", "spiral", "figure8"]
for sid, shape in enumerate(shapes):
    motion = engine.motion_states[sid]
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = shape
    traj.shape_params = {"radius": 2.0, "scale": 2.0, "height": 2.0}
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = 0.5
    traj.center = np.zeros(3)
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ {shape} configurado para fuente {sid}")

# Guardar posiciones iniciales
initial = {}
for sid in range(3):
    initial[sid] = engine._positions[sid].copy()

print("\n🏃 Simulando SIN procesamiento manual de deltas...")
print("   (engine.update() debe hacerlo automáticamente)")

# SOLO llamar a engine.update(), sin procesar deltas manualmente
for frame in range(60):  # 1 segundo
    engine.update()  # ¡Sin parámetros, sin procesamiento manual!
    
    if frame % 20 == 0:
        print(f"\n  Frame {frame}:")
        for sid, shape in enumerate(shapes):
            pos = engine._positions[sid]
            dist = np.linalg.norm(pos - initial[sid])
            print(f"    {shape}: distancia = {dist:.3f}")

# Verificar resultados
print("\n📊 RESULTADOS FINALES:")
success = True
for sid, shape in enumerate(shapes):
    final_pos = engine._positions[sid]
    dist = np.linalg.norm(final_pos - initial[sid])
    
    if dist > 0.1:
        print(f"  ✅ {shape}: Se movió {dist:.3f} unidades AUTOMÁTICAMENTE")
    else:
        print(f"  ❌ {shape}: NO se movió (dist={dist:.3f})")
        success = False

if success:
    print("\n🎉 ¡ÉXITO TOTAL!")
    print("   engine.update() procesa deltas automáticamente")
    print("   No más procesamiento manual en tests")
    print("\n📝 Próximo paso: Migrar MacroTrajectory a deltas")
else:
    print("\n❌ El procesamiento automático no funciona")
