# === test_deltas_final_working.py ===
# 🧪 Test final - DEBE funcionar

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🎉 TEST FINAL - DELTAS FUNCIONANDO")
print("="*60)

# Setup
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=1)
engine._positions[0] = np.array([10.0, 0.0, 0.0])

print(f"📍 Posición inicial: {engine._positions[0]}")

# Concentración
engine.set_macro_concentration(macro, factor=0.5)
print("✅ Concentración aplicada")

# Update
print("\n🔄 Actualizando 20 frames...")
for i in range(20):
    pos_before = engine._positions[0].copy()
    engine.update()
    pos_after = engine._positions[0]
    
    if not np.array_equal(pos_before, pos_after):
        print(f"   Frame {i+1}: ¡SE MOVIÓ! {pos_before} → {pos_after}")
        break
    elif i == 19:
        print("   ❌ No se movió en 20 frames")

print(f"\n📊 Posición final: {engine._positions[0]}")
print(f"📏 Distancia al centro: {np.linalg.norm(engine._positions[0]):.2f}")

if np.linalg.norm(engine._positions[0]) < 9.9:
    print("\n🎉 ¡ÉXITO! EL SISTEMA DE DELTAS FUNCIONA")
else:
    print("\n❌ Las fuentes no se movieron")