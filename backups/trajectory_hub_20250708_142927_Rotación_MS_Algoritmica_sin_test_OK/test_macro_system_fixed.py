# === test_macro_system_fixed.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
import math

print("🧪 TEST FINAL: Sistema de Macros Arreglado\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Verificar que _macros existe
print("1️⃣ Verificando inicialización:")
if hasattr(engine, '_macros'):
    print("  ✅ engine._macros existe")
else:
    print("  ❌ engine._macros NO existe")
    exit(1)

# Crear macro
print("\n2️⃣ Creando macro...")
engine.create_macro("test", [0, 1, 2])

# Verificar que se creó
if "test" in engine._macros:
    print("  ✅ Macro 'test' creado")
    macro = engine._macros["test"]
    print(f"  - source_ids: {macro.source_ids}")
    print(f"  - trajectory_component: {hasattr(macro, 'trajectory_component')}")
else:
    print("  ❌ Macro NO se creó")
    exit(1)

# Verificar motion_states
print("\n3️⃣ Verificando motion_states:")
for sid in [0, 1, 2]:
    if sid in engine.motion_states:
        components = list(engine.motion_states[sid].active_components.keys())
        print(f"  Fuente {sid}: {components}")

# Configurar trayectoria
print("\n4️⃣ Configurando trayectoria circular...")
def circular_traj(t):
    return np.array([5 * np.cos(t), 5 * np.sin(t), 0])

engine.set_macro_trajectory("test", circular_traj)
print("  ✅ Trayectoria configurada")

# Test de movimiento
print("\n5️⃣ Test de movimiento (60 frames):")
pos_start = engine._positions[0].copy()

for i in range(60):
    engine.update()
    
    if i % 20 == 19:
        pos = engine._positions[0]
        dist = np.linalg.norm(pos - pos_start)
        print(f"  Frame {i+1}: distancia = {dist:.3f}")

pos_final = engine._positions[0]
total_dist = np.linalg.norm(pos_final - pos_start)

if total_dist > 0.1:
    print(f"\n🎉 ¡ÉXITO TOTAL! Movimiento = {total_dist:.3f} unidades")
    print("✅ MacroTrajectory funciona perfectamente con deltas")
else:
    print(f"\n❌ Sin movimiento significativo: {total_dist:.6f}")
