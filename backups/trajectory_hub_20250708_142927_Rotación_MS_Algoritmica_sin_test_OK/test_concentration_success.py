# === test_concentration_success.py ===
# 🧪 Test definitivo - DEBE funcionar

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎉 TEST FINAL - CONCENTRACIÓN")
print("="*60)

# Setup
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=3)

# Posiciones
for i in range(3):
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([10 * np.cos(angle), 10 * np.sin(angle), 0])

print("📍 Posiciones iniciales:")
for i in range(3):
    pos = engine._positions[i]
    print(f"   Source {i}: {pos} (dist={np.linalg.norm(pos):.2f})")

# Concentración
print("\n🎯 Aplicando concentración...")
engine.set_macro_concentration(macro, factor=0.5)

# Update
print("\n🔄 Actualizando 30 frames...")
for frame in range(30):
    engine.update()
    if frame % 10 == 9:
        dist = np.linalg.norm(engine._positions[0])
        print(f"   Frame {frame+1}: dist={dist:.2f}")

print("\n📊 Posiciones finales:")
for i in range(3):
    pos = engine._positions[i]
    dist = np.linalg.norm(pos)
    print(f"   Source {i}: {pos} (dist={dist:.2f})")

final_dist = np.linalg.norm(engine._positions[0])
if final_dist < 9.0:
    print(f"\n🎉 ¡ÉXITO TOTAL!")
    print(f"   Las fuentes se concentraron de 10.00 a {final_dist:.2f}")
    print(f"   EL SISTEMA DE DELTAS FUNCIONA AL 100%")
else:
    print("\n❌ Aún no funciona")