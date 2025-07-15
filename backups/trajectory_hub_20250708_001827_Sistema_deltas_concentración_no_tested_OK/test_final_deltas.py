# === test_final_deltas.py ===
# 🧪 Test final del sistema de deltas

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎉 TEST FINAL - SISTEMA DE DELTAS")
print("="*60)

# Setup
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=3)

# Posiciones en círculo
for i in range(3):
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([10 * np.cos(angle), 10 * np.sin(angle), 0])

print("📍 Posiciones iniciales:")
for i in range(3):
    pos = engine._positions[i]
    print(f"   Source {i}: {pos} (dist={np.linalg.norm(pos):.2f})")

# Concentración
print("\n🎯 Aplicando concentración (factor=0.5)...")
engine.set_macro_concentration(macro, factor=0.5)

# Actualizar
print("\n🔄 Actualizando 30 frames...")
for frame in range(30):
    engine.update()
    if frame % 10 == 9:
        print(f"   Frame {frame+1}: dist={np.linalg.norm(engine._positions[0]):.2f}")

print("\n📊 Posiciones finales:")
for i in range(3):
    pos = engine._positions[i]
    dist = np.linalg.norm(pos)
    print(f"   Source {i}: {pos} (dist={dist:.2f})")
    
if dist < 9.0:
    print("\n🎉 ¡ÉXITO! El sistema de deltas FUNCIONA")
else:
    print("\n❌ Las fuentes no se movieron")