# === verify_fix.py ===
# Verifica que el fix funcionó

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test directo del método
print("🧪 Verificando fix de calculate_delta...")

try:
    from trajectory_hub.core.motion_components import IndividualTrajectory, MotionState
    import numpy as np
    
    # Crear instancia
    traj = IndividualTrajectory()
    traj.shape = "circle"
    traj.movement_speed = 1.0
    traj.enabled = True
    traj.radius = 2.0
    traj.position_on_trajectory = 0.0
    
    # Crear estado
    state = MotionState()
    state.position = np.array([0.0, 0.0, 0.0])
    
    # Probar calculate_delta con 4 argumentos
    delta = traj.calculate_delta(state, 1.0, 0.1)
    
    if delta is not None:
        print("✅ calculate_delta funciona con 4 argumentos")
        print(f"   Delta position: {delta.position}")
    else:
        print("⚠️ calculate_delta retornó None")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test completo
print("\n🧪 Test completo con engine...")
from trajectory_hub import EnhancedTrajectoryEngine

engine = EnhancedTrajectoryEngine(max_sources=3, fps=60, enable_modulator=False)
macro_name = engine.create_macro("test", source_count=1)
macro = engine._macros[macro_name]
sid = list(macro.source_ids)[0]

try:
    engine.set_individual_trajectory(
        macro_name, sid,
        shape="circle",
        shape_params={'radius': 2.0},
        movement_mode="fix",
        speed=1.0
    )
    print("✅ Trayectoria configurada")
    
    # Ejecutar un update
    engine.update()
    print("✅ Update ejecutado sin errores")
    
except Exception as e:
    print(f"❌ Error en test completo: {e}")
