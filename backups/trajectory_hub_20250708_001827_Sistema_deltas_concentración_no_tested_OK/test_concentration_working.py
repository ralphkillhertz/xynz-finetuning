# === test_concentration_working.py ===
# 🧪 Test simple de concentración

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎉 TEST DE CONCENTRACIÓN")
print("="*60)

# Setup
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=1)
engine._positions[0] = np.array([10.0, 0.0, 0.0])

print(f"📍 Inicial: {engine._positions[0]}")

# Concentración
engine.set_macro_concentration(macro, factor=0.5)

# Update
for _ in range(10):
    engine.update()

print(f"📍 Final: {engine._positions[0]}")

dist = np.linalg.norm(engine._positions[0])
if dist < 9.9:
    print(f"\n🎉 ¡FUNCIONA! Distancia: {dist:.2f}")
else:
    print(f"\n❌ No funciona. Distancia: {dist:.2f}")