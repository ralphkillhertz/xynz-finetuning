# === test_individual_minimal.py ===
# Test minimal de trayectorias individuales

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60, enable_modulator=False)
print("✅ Engine creado")

# Crear macro
macro_name = engine.create_macro("test", source_count=2)
macro = engine._macros[macro_name]
sid = list(macro.source_ids)[0]
print(f"✅ Macro '{macro_name}' con fuente {sid}")

# Configurar trayectoria individual
try:
    engine.set_individual_trajectory(
        macro_name, 
        sid,
        shape="circle",
        shape_params={'radius': 3.0},
        movement_mode="fix",
        speed=1.0
    )
    print("✅ Trayectoria configurada")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Verificar componente
motion = engine.motion_states[sid]
if 'individual_trajectory' in motion.active_components:
    traj = motion.active_components['individual_trajectory']
    print(f"✅ Componente creado: {type(traj).__name__}")
    print(f"   - shape: {getattr(traj, 'shape', 'N/A')}")
    print(f"   - enabled: {getattr(traj, 'enabled', False)}")
    print(f"   - speed: {getattr(traj, 'movement_speed', 0)}")

# Test rápido de movimiento
initial_pos = engine._positions[sid].copy()
for _ in range(20):
    engine.update()

final_pos = engine._positions[sid]
distance = np.linalg.norm(final_pos - initial_pos)
print(f"\n{'✅' if distance > 0.01 else '❌'} Distancia recorrida: {distance:.3f}")
