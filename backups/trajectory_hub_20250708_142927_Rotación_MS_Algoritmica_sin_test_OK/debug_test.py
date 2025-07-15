# === debug_test.py ===
# Debug detallado del problema

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine

# Crear engine y configurar
engine = EnhancedTrajectoryEngine(max_sources=3, fps=60, enable_modulator=False)
macro_name = engine.create_macro("test", source_count=1)
sid = list(engine._macros[macro_name].source_ids)[0]

# Configurar trayectoria
engine.set_individual_trajectory(
    macro_name, sid,
    shape="circle",
    shape_params={'radius': 2.0},
    movement_mode="fix",
    speed=1.0
)

# Debug: Ver qué tiene el objeto
motion = engine.motion_states[sid]
if 'individual_trajectory' in motion.active_components:
    traj = motion.active_components['individual_trajectory']
    
    print("🔍 DEBUG - Atributos de IndividualTrajectory:")
    attrs = [attr for attr in dir(traj) if not attr.startswith('_')]
    for attr in sorted(attrs):
        try:
            value = getattr(traj, attr)
            if not callable(value):
                print(f"  - {attr}: {value}")
        except:
            pass
    
    # Verificar específicamente shape_params
    print("\n🔍 shape_params existe:", hasattr(traj, 'shape_params'))
    if hasattr(traj, 'shape_params'):
        print(f"   Valor: {traj.shape_params}")
    else:
        print("   ❌ NO EXISTE")
        print("\n   Intentando añadirlo manualmente...")
        traj.shape_params = {'radius': 2.0}
        print("   ✅ Añadido manualmente")
    
    # Probar un update
    try:
        print("\n🧪 Probando update...")
        engine.update()
        print("✅ Update ejecutado sin errores")
    except Exception as e:
        print(f"❌ Error: {e}")
