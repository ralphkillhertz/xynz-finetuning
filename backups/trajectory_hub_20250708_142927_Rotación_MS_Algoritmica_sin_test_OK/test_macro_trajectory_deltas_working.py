# === test_macro_trajectory_deltas_working.py ===
import numpy as np
import time
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test de MacroTrajectory con sistema de deltas...")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
print("\n1️⃣ Creando macro 'orbita'...")
engine.create_macro("orbita", [0, 1, 2, 3, 4])

# Configurar trayectoria circular
print("\n2️⃣ Configurando trayectoria circular...")
try:
    engine.set_macro_trajectory("orbita", "circular", speed=2.0)
    print("✅ Trayectoria configurada")
except Exception as e:
    print(f"❌ Error configurando trayectoria: {e}")
    exit(1)

# Verificar componentes
print("\n3️⃣ Verificando componentes...")
for sid in range(5):
    if sid in engine.motion_states:
        motion = engine.motion_states[sid]
        components = list(motion.active_components.keys())
        print(f"  Fuente {sid}: {components}")

# Test de movimiento
print("\n4️⃣ Probando movimiento (2 segundos)...")
positions_start = {}
for sid in range(5):
    positions_start[sid] = engine._positions[sid].copy()
    print(f"  Fuente {sid} empieza en: {positions_start[sid]}")

# Simular 2 segundos
start_time = time.time()
frames = 0
while time.time() - start_time < 2.0:
    engine.update()
    frames += 1
    time.sleep(1/60)  # 60 FPS

print(f"\n✅ {frames} frames procesados")

# Verificar movimiento final
print("\n5️⃣ Verificando posiciones finales:")
all_moved = True
for sid in range(5):
    pos_final = engine._positions[sid]
    distance = np.linalg.norm(pos_final - positions_start[sid])
    
    if distance > 0.1:
        print(f"  ✅ Fuente {sid}: movió {distance:.2f} unidades")
    else:
        print(f"  ❌ Fuente {sid}: NO se movió (dist={distance:.4f})")
        all_moved = False

if all_moved:
    print("\n🎉 ¡ÉXITO TOTAL! MacroTrajectory funciona con deltas")
else:
    print("\n⚠️ Algunas fuentes no se movieron")
    
# Test adicional: cambiar tipo de trayectoria
print("\n6️⃣ Probando cambio de trayectoria...")
engine.set_macro_trajectory("orbita", "figure_eight", speed=1.5)
pos_before = engine._positions[0].copy()

for _ in range(60):  # 1 segundo
    engine.update()
    
pos_after = engine._positions[0].copy()
if np.linalg.norm(pos_after - pos_before) > 0.1:
    print("✅ Figure eight también funciona")
else:
    print("❌ Figure eight no genera movimiento")

print("\n✅ Test completado")
