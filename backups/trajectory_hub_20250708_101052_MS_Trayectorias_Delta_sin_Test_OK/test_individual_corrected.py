# === test_individual_corrected.py ===
from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("🧪 Test corregido de IndividualTrajectory...")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro - esto crea fuentes con nombres como "test_0", "test_1", etc.
engine.create_macro("test", [0, 1, 2])

# Los motion_states usan nombres, no IDs numéricos
source_names = ["test_0", "test_1", "test_2"]

# Configurar trayectorias usando los NOMBRES correctos
print("\nConfigurando trayectorias...")
for i, name in enumerate(source_names):
    try:
        engine.set_individual_trajectory(name, "circle", "fix", 
                                       radius=1.0 + i*0.5, speed=0.5)
        print(f"  ✅ {name} configurada")
    except Exception as e:
        print(f"  ❌ Error con {name}: {e}")

# Guardar posiciones iniciales
initial_pos = {}
for i in range(3):
    initial_pos[i] = engine._positions[i].copy()

print("\nPosiciones iniciales:")
for i in range(3):
    print(f"  Fuente {i}: {initial_pos[i]}")

# Simular
print("\nSimulando...")
for frame in range(60):
    engine.update(1/60)

# Verificar movimiento
print("\nResultados:")
for i in range(3):
    dist = np.linalg.norm(engine._positions[i] - initial_pos[i])
    status = "✅ MOVIDA" if dist > 0.01 else "❌ ESTÁTICA"
    print(f"  Fuente {i}: {status} (dist: {dist:.3f})")
