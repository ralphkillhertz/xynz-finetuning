# === test_macro_trajectory_fixed.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test MacroTrajectory con deltas (CORREGIDO)...")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
print("\n1️⃣ Creando macro...")
engine.create_macro("test", [0, 1, 2, 3, 4])

# Ver parámetros correctos
print("\n2️⃣ Configurando trayectoria...")
# NO usar speed como parámetro, usar trajectory_params
engine.set_macro_trajectory(
    "test", 
    trajectory_type="circular",
    trajectory_params={'radius': 5.0, 'speed': 2.0}
)
print("✅ Trayectoria configurada")

# Guardar posiciones iniciales
print("\n3️⃣ Posiciones iniciales:")
pos_start = {}
for i in range(5):
    pos_start[i] = engine._positions[i].copy()
    print(f"  Fuente {i}: {pos_start[i]}")

# Ejecutar movimiento
print("\n4️⃣ Ejecutando 120 frames (2 segundos)...")
for frame in range(120):
    engine.update()
    
    # Mostrar progreso cada 30 frames
    if frame % 30 == 29:
        dist = np.linalg.norm(engine._positions[0] - pos_start[0])
        print(f"  Frame {frame+1}: Fuente 0 movió {dist:.3f} unidades")

# Verificar resultados
print("\n5️⃣ Resultados finales:")
total_movement = 0
for i in range(5):
    pos_final = engine._positions[i]
    dist = np.linalg.norm(pos_final - pos_start[i])
    total_movement += dist
    
    status = "✅" if dist > 0.1 else "❌"
    print(f"  {status} Fuente {i}: {dist:.3f} unidades")

avg_movement = total_movement / 5
if avg_movement > 0.1:
    print(f"\n🎉 ÉXITO - Movimiento promedio: {avg_movement:.3f} unidades")
else:
    print(f"\n❌ FALLO - Movimiento promedio: {avg_movement:.3f} unidades")
    
    # Debug adicional
    print("\n🔍 Debug:")
    if 0 in engine.motion_states:
        motion = engine.motion_states[0]
        print(f"  Componentes activos: {list(motion.active_components.keys())}")
        
        if 'macro_trajectory' in motion.active_components:
            mt = motion.active_components['macro_trajectory']
            print(f"  MacroTrajectory.enabled: {mt.enabled}")
            print(f"  MacroTrajectory.phase: {mt.phase}")
            print(f"  MacroTrajectory.speed: {mt.speed}")
