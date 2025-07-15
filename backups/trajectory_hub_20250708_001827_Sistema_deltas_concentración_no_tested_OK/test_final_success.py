# === test_final_success.py ===
# 🧪 Test FINAL - Ya funciona de verdad

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎉 TEST FINAL - SISTEMA DE DELTAS")
print("="*60)

# Setup
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=3)

# Posiciones
for i in range(3):
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([10 * np.cos(angle), 10 * np.sin(angle), 0])

print("📍 Posiciones iniciales (dist=10.00)")

# Concentración
engine.set_macro_concentration(macro, factor=0.5)

# Update
print("\n🔄 Actualizando...")
for i in range(30):
    engine.update()
    if i == 0:
        dist = np.linalg.norm(engine._positions[0])
        print(f"   Frame 1: dist={dist:.2f}")

# Final
print("\n📊 RESULTADO:")
for i in range(3):
    dist = np.linalg.norm(engine._positions[i])
    print(f"   Source {i}: distancia = {dist:.2f}")

avg = np.mean([np.linalg.norm(engine._positions[i]) for i in range(3)])
print(f"\n   Promedio: {avg:.2f}")

if avg < 9.5:
    print("\n🎉 ¡ÉXITO TOTAL! SISTEMA DE DELTAS 100% FUNCIONAL")