# === test_super_simple.py ===
# 🧪 Test ultra simple para verificar

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

# Crear engine
engine = EnhancedTrajectoryEngine()

# Crear un macro simple
macro = engine.create_macro("test", 1)

# Posición inicial
engine._positions[0] = np.array([1.0, 0.0, 0.0])
print(f"Antes: {engine._positions[0]}")

# Intentar rotación
try:
    engine.set_macro_rotation("test", speed_y=1.0)
    engine.update()
    print(f"Después: {engine._positions[0]}")
except Exception as e:
    print(f"Error: {e}")
    
    # Debug manual
    if 0 in engine.motion_states:
        motion = engine.motion_states[0]
        if 'macro_rotation' in motion.active_components:
            rot = motion.active_components['macro_rotation']
            # Configurar manualmente
            rot.speed_y = 1.0
            rot.enabled = True
            print("Configurado manualmente")
            
            # Un update manual
            delta = rot.calculate_delta(motion, 0, 0.016)
            print(f"Delta: {delta.position}")