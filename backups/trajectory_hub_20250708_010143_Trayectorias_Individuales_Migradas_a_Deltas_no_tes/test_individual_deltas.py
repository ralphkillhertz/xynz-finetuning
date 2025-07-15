# === test_individual_deltas.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import time

print("🧪 Test de IndividualTrajectory con sistema de deltas...")

# Crear engine
engine = EnhancedTrajectoryEngine(n_sources=5, update_rate=60)

# Crear macro con 3 fuentes
engine.create_macro("test", [0, 1, 2])

# Configurar trayectorias individuales (círculos)
engine.set_individual_trajectories("test", 
    trajectories={
        0: {"shape": "circle", "params": {"radius": 2.0}},
        1: {"shape": "circle", "params": {"radius": 1.5}},
        2: {"shape": "circle", "params": {"radius": 1.0}}
    }
)

# Activar movimiento
for sid in [0, 1, 2]:
    engine.set_individual_trajectory("test", sid, 
        mode="fix", 
        speed=0.5,
        shape="circle"
    )

print("\nPosiciones iniciales:")
for sid in [0, 1, 2]:
    pos = engine._positions[sid]
    print(f"  Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

# Simular 2 segundos
print("\nSimulando movimiento...")
for i in range(120):  # 2 segundos a 60 fps
    engine.update(1/60)
    if i % 30 == 0:  # Cada 0.5 segundos
        print(f"\nT={i/60:.1f}s:")
        for sid in [0, 1, 2]:
            pos = engine._positions[sid]
            print(f"  Fuente {sid}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

print("\n✅ Si las posiciones cambiaron, las trayectorias individuales funcionan con deltas!")
