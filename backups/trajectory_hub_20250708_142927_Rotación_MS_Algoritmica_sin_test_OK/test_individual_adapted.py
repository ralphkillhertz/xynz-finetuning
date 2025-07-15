# === test_individual_adapted.py ===
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import IndividualTrajectory, TrajectoryMovementMode
import numpy as np
import time

print("🧪 Test adaptado de IndividualTrajectory...")

# Setup
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60)
engine.create_macro("test", [0, 1, 2])

# Configurar trayectorias
for i, sid in enumerate([0, 1, 2]):
    motion = engine.motion_states[sid]
    traj = IndividualTrajectory()
    traj.enabled = True
    traj.shape_type = "circle"
    traj.shape_params = {"radius": 1.0 + i * 0.5}
    traj.movement_mode = TrajectoryMovementMode.FIX
    traj.movement_speed = 0.5
    traj.center = np.zeros(3)
    motion.active_components['individual_trajectory'] = traj
    print(f"✅ Trayectoria configurada para fuente {sid}")

# Ver qué parámetros espera update_with_deltas
motion = engine.motion_states[0]
print("\n🔍 Inspeccionando update_with_deltas...")
import inspect
try:
    sig = inspect.signature(motion.update_with_deltas)
    print(f"   Firma: {sig}")
except:
    print("   No se pudo obtener firma")

# Probar diferentes formas de llamarlo
print("\n🧪 Probando diferentes llamadas...")

# Opción 1: Solo current_time
try:
    current_time = time.time()
    deltas = motion.update_with_deltas(current_time)
    print(f"✅ Funciona con current_time: {len(deltas)} deltas")
except Exception as e:
    print(f"❌ Con current_time: {e}")

# Opción 2: current_time y dt
try:
    current_time = time.time()
    dt = 1/60
    deltas = motion.update_with_deltas(current_time, dt)
    print(f"✅ Funciona con current_time y dt: {len(deltas)} deltas")
except Exception as e:
    print(f"❌ Con current_time y dt: {e}")

# Usar la forma que funcionó
print("\n🏃 Simulación adaptada...")
initial = {}
for sid in [0, 1, 2]:
    initial[sid] = engine._positions[sid].copy()

# Simular con el método correcto
start_time = time.time()
for frame in range(60):  # 1 segundo
    current_time = start_time + frame/60
    
    for sid in [0, 1, 2]:
        motion = engine.motion_states[sid]
        
        # Intentar con la firma que esperamos
        try:
            # Si espera current_time, calcular dt internamente
            if hasattr(motion.state, 'last_update'):
                dt = current_time - motion.state.last_update
                motion.state.last_update = current_time
            else:
                dt = 1/60
                motion.state.last_update = current_time
            
            # Actualizar componentes manualmente si es necesario
            traj = motion.active_components.get('individual_trajectory')
            if traj and hasattr(traj, 'update_position'):
                # Actualizar posición
                old_phase = traj.position_on_trajectory
                traj.update_position(dt)
                
                # Calcular nueva posición
                if hasattr(traj, '_calculate_position_on_trajectory'):
                    new_pos = traj._calculate_position_on_trajectory(traj.position_on_trajectory)
                    old_pos = traj._calculate_position_on_trajectory(old_phase)
                    
                    # Aplicar delta directamente
                    delta_pos = new_pos - old_pos
                    engine._positions[sid] += delta_pos
                    
        except Exception as e:
            if frame == 0:
                print(f"❌ Error en simulación: {e}")

# Resultados
print("\n📊 Resultados:")
for sid in [0, 1, 2]:
    dist = np.linalg.norm(engine._positions[sid] - initial[sid])
    status = "✅" if dist > 0.1 else "❌"
    print(f"  Fuente {sid}: {status} Movió {dist:.3f}")

# Si no funciona con deltas, al menos sabemos que el componente funciona
if all(np.linalg.norm(engine._positions[sid] - initial[sid]) > 0.1 for sid in [0, 1, 2]):
    print("\n✅ ¡Las trayectorias funcionan!")
    print("\n📝 Nota: Necesitamos adaptar update_with_deltas o crear uno nuevo")
