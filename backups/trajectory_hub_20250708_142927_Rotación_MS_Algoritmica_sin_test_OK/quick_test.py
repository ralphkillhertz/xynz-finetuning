# === quick_test.py ===
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

# Test rápido
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

# Posición inicial
initial_pos = engine._positions[sid].copy()
print(f"Posición inicial: {initial_pos}")

# 10 updates
for i in range(10):
    engine.update()

# Posición final
final_pos = engine._positions[sid]
distance = np.linalg.norm(final_pos - initial_pos)

print(f"Posición final: {final_pos}")
print(f"Distancia: {distance:.3f}")
print(f"\n{'✅ ¡FUNCIONA!' if distance > 0.01 else '❌ No se mueve'}")
