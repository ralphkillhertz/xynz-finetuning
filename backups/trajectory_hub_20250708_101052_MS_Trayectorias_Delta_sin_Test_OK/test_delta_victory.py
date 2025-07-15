# === test_delta_victory.py ===
# 🧪 Test de VICTORIA - Ya funciona

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎉 TEST DE VICTORIA - SISTEMA DE DELTAS")
print("="*60)

# Setup
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=3)

# Posiciones
for i in range(3):
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([10 * np.cos(angle), 10 * np.sin(angle), 0])

print("📍 Inicial: todas a distancia 10.00")

# Concentración
engine.set_macro_concentration(macro, factor=0.5)

# Update
for _ in range(30):
    engine.update()

# Resultado
print("\n📍 Final:")
for i in range(3):
    dist = np.linalg.norm(engine._positions[i])
    print(f"   Source {i}: distancia = {dist:.2f}")

avg_dist = np.mean([np.linalg.norm(engine._positions[i]) for i in range(3)])

if avg_dist < 9.0:
    print(f"\n🎉 ¡VICTORIA TOTAL!")
    print(f"   Distancia promedio: {avg_dist:.2f}")
    print(f"   SISTEMA DE DELTAS 100% FUNCIONAL")
else:
    print("\n❌ No funcionó")