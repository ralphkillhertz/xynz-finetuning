# === diagnose_component_type.py ===
# 🔍 Diagnóstico del tipo de componente

import sys
sys.path.append('.')

from trajectory_hub import EnhancedTrajectoryEngine

# Crear engine y macro
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)
for i in range(4):
    engine.create_source(f"test_{i}")

engine.create_macro("test", 4)
engine.set_macro_rotation("test", speed_y=1.0)

# Inspeccionar
for sid in range(4):
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        print(f"\n📍 Fuente {sid}:")
        print(f"   motion type: {type(motion)}")
        
        if hasattr(motion, 'active_components'):
            print(f"   active_components type: {type(motion.active_components)}")
            for name, comp in motion.active_components.items():
                print(f"   - {name}: {type(comp)}")
                if hasattr(comp, 'enabled'):
                    print(f"     enabled: {comp.enabled}")
                if hasattr(comp, 'calculate_delta'):
                    print(f"     has calculate_delta: ✓")