# === test_final_concentration.py ===
# 🧪 Test final con todo funcionando

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎉 TEST FINAL DE CONCENTRACIÓN")
print("="*60)

# Setup
engine = EnhancedTrajectoryEngine()
macro_name = engine.create_macro("test", source_count=3)

# Posiciones iniciales
for i in range(3):
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([10 * np.cos(angle), 10 * np.sin(angle), 0])
    print(f"Source {i}: {engine._positions[i]}")

# Aplicar concentración
print("\n🎯 Aplicando concentración...")
engine.set_macro_concentration(macro_name, factor=0.5)

# Actualizar
print("\n🔄 Actualizando 10 frames...")
for i in range(10):
    engine.update()

# Resultado
print("\n📊 RESULTADO:")
for i in range(3):
    dist = np.linalg.norm(engine._positions[i])
    print(f"Source {i}: distancia al centro = {dist:.2f}")

if dist < 9.0:
    print("\n🎉 ¡ÉXITO! Las fuentes se están concentrando")
else:
    print("\n❌ Las fuentes no se movieron")