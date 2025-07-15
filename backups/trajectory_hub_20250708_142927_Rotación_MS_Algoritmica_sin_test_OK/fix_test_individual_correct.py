# === fix_test_individual_correct.py ===
# 🔧 Fix: Test corregido con argumentos válidos
# ⚡ Usa la API correcta del engine

test_code = '''# === test_individual_deltas_fixed.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import time

print("🧪 Test de IndividualTrajectory con sistema de deltas...")

# Crear engine con argumentos correctos
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Crear macro con 3 fuentes
engine.create_macro("test", [0, 1, 2])

# Configurar trayectorias individuales
print("\\nConfigurando trayectorias individuales...")
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

print("\\nPosiciones iniciales:")
for sid in [0, 1, 2]:
    pos = engine._positions[sid]
    print(f"  Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

# Simular 2 segundos
print("\\nSimulando movimiento...")
for i in range(120):  # 2 segundos a 60 fps
    engine.update(1/60)
    
    if i % 30 == 0:  # Cada 0.5 segundos
        print(f"\\nT={i/60:.1f}s:")
        for sid in [0, 1, 2]:
            pos = engine._positions[sid]
            print(f"  Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")
            
            # Debug: verificar estado del componente
            if sid in engine.motion_states:
                motion = engine.motion_states[sid]
                if 'individual_trajectory' in motion.active_components:
                    traj = motion.active_components['individual_trajectory']
                    print(f"    Phase: {getattr(traj, 'position_on_trajectory', 0):.2f}")

print("\\n✅ Test completado!")

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
'''

with open("test_individual_deltas_fixed.py", "w") as f:
    f.write(test_code)

print("✅ Test corregido creado: test_individual_deltas_fixed.py")
print("\n📝 También vamos a crear un test de diagnóstico:")

# Test de diagnóstico
diag_code = '''# === diagnose_individual_update.py ===
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
print(f"\\n✅ SourceMotion creado para fuente {sid}")
print(f"  Componentes activos: {list(motion.active_components.keys())}")

if 'individual_trajectory' in motion.active_components:
    traj = motion.active_components['individual_trajectory']
    print(f"\\n✅ IndividualTrajectory encontrado")
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
        print(f"\\n🧪 Test directo de calculate_delta:")
        delta = traj.calculate_delta(motion.state, 0.1)
        print(f"  Delta position: {delta.position}")
        print(f"  Position on trajectory: {traj.position_on_trajectory}")
        
        # Test update_with_deltas
        print(f"\\n🧪 Test de update_with_deltas:")
        deltas = motion.update_with_deltas(0.1)
        print(f"  Número de deltas: {len(deltas)}")
        for i, d in enumerate(deltas):
            print(f"  Delta {i}: {d.position}")
else:
    print("❌ No se encontró individual_trajectory en los componentes")
'''

with open("diagnose_individual_update.py", "w") as f:
    f.write(diag_code)

print("📝 Diagnóstico creado: diagnose_individual_update.py")