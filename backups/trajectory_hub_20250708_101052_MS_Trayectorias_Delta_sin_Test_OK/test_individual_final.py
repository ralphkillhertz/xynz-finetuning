# === test_individual_final.py ===
import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 Test FINAL de IndividualTrajectory con deltas...")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

# Crear macro
engine.create_macro("test", [0, 1, 2])

# Configurar trayectorias individuales usando el método correcto
print("\nConfigurando trayectorias...")
for i, sid in enumerate([0, 1, 2]):
    engine.set_individual_trajectory("test", sid,
        shape="circle",
        mode="fix",
        speed=0.5,
        radius=1.0 + i * 0.5  # Radios diferentes
    )
    print(f"  ✅ Fuente {sid} configurada")

# Guardar posiciones iniciales
initial_positions = {}
for sid in [0, 1, 2]:
    initial_positions[sid] = engine._positions[sid].copy()
    print(f"\nPosición inicial {sid}: {initial_positions[sid]}")

# Simular movimiento
print("\n🏃 Simulando 2 segundos...")
for frame in range(120):  # 2 segundos a 60 fps
    engine.update(1/60)
    
    # Mostrar progreso cada 0.5 segundos
    if frame % 30 == 0:
        print(f"\nT = {frame/60:.1f}s:")
        for sid in [0, 1, 2]:
            pos = engine._positions[sid]
            moved = np.linalg.norm(pos - initial_positions[sid])
            print(f"  Fuente {sid}: {pos} (movido: {moved:.3f})")

# Verificación final
print("\n📊 Resultados:")
all_moved = True
for sid in [0, 1, 2]:
    distance = np.linalg.norm(engine._positions[sid] - initial_positions[sid])
    status = "✅" if distance > 0.1 else "❌"
    print(f"  Fuente {sid}: {status} Distancia movida: {distance:.3f}")
    if distance < 0.1:
        all_moved = False

if all_moved:
    print("\n🎉 ¡ÉXITO! Las trayectorias individuales funcionan con deltas!")
else:
    print("\n⚠️ Algunas fuentes no se movieron. Revisar implementación.")
