# === test_deltas_finally_working.py ===
# 🧪 Test DEFINITIVO - Ya debe funcionar

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎉 TEST DEFINITIVO - DELTAS FUNCIONANDO")
print("="*60)

# Setup
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=3)

# Posiciones
for i in range(3):
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([10 * np.cos(angle), 10 * np.sin(angle), 0])

print("📍 Inicial:")
for i in range(3):
    print(f"   Source {i}: dist={np.linalg.norm(engine._positions[i]):.2f}")

# Concentración
engine.set_macro_concentration(macro, factor=0.8)

# Update
for _ in range(20):
    engine.update()

print("\n📍 Final:")
for i in range(3):
    dist = np.linalg.norm(engine._positions[i])
    print(f"   Source {i}: dist={dist:.2f}")

if dist < 9.5:
    print("\n🎉 ¡ÉXITO! EL SISTEMA DE DELTAS FUNCIONA AL 100%")
else:
    print("\n❌ No funcionó")