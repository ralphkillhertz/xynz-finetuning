# === test_concentration_animate.py ===
# 🔧 Test usando animate_macro_concentration correctamente
# ⚡ Este podría ser el método REAL de concentración

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 TEST ANIMATE_MACRO_CONCENTRATION")
print("="*60)

# 1. Setup
engine = EnhancedTrajectoryEngine()
macro_name = engine.create_macro("test", source_count=3)
source_ids = [0, 1, 2]

# 2. Posiciones iniciales
print("\n📍 Estableciendo posiciones (radio=10)...")
angles = np.linspace(0, 2*np.pi, 4)[:-1]
for i in source_ids:
    engine._positions[i] = np.array([
        10 * np.cos(angles[i]),
        10 * np.sin(angles[i]),
        0
    ])
    print(f"   Source {i}: {engine._positions[i]}")

# 3. Aplicar concentración base
center = np.array([0, 0, 0])
engine.apply_concentration(macro_name, center)
print("\n✅ Concentración preparada")

# 4. Guardar posiciones
pos_before = {i: engine._positions[i].copy() for i in source_ids}
distances_before = [np.linalg.norm(engine._positions[i]) for i in source_ids]
print(f"\n📏 Distancias iniciales al centro: {[f'{d:.2f}' for d in distances_before]}")

# 5. ANIMAR concentración con target_factor
print("\n🎬 Animando concentración...")
target_factor = 0.2  # Concentrar al 20% de la distancia original
try:
    engine.animate_macro_concentration(macro_name, target_factor)
    print(f"✅ Animación iniciada (target_factor={target_factor})")
except Exception as e:
    print(f"❌ Error: {e}")

# 6. Actualizar muchos frames
print("\n🔄 Actualizando 30 frames...")
for frame in range(30):
    engine.update()
    
    # Checkpoints cada 10 frames
    if frame % 10 == 9:
        print(f"\n   Frame {frame+1}:")
        for i in source_ids:
            current_dist = np.linalg.norm(engine._positions[i])
            original_dist = distances_before[i]
            reduction = (original_dist - current_dist) / original_dist * 100
            print(f"     Source {i}: distancia={current_dist:.2f} (reducción={reduction:.1f}%)")

# 7. Resultado final
print("\n📊 RESULTADO FINAL:")
print("-"*50)
any_movement = False
for i in source_ids:
    before = pos_before[i]
    after = engine._positions[i]
    movement = np.linalg.norm(after - before)
    
    dist_before = distances_before[i]
    dist_after = np.linalg.norm(after)
    
    print(f"\nSource {i}:")
    print(f"  Posición: {before} → {after}")
    print(f"  Distancia al centro: {dist_before:.2f} → {dist_after:.2f}")
    print(f"  Movimiento total: {movement:.4f}")
    
    if movement > 0.001:
        print("  ✅ SE MOVIÓ")
        any_movement = True
    else:
        print("  ❌ NO SE MOVIÓ")

if any_movement:
    print("\n🎉 ¡ÉXITO! Las fuentes se están concentrando")
    
    # Verificar si llegaron al target
    expected_distances = [d * target_factor for d in distances_before]
    print(f"\n🎯 Distancias esperadas (factor={target_factor}): {[f'{d:.2f}' for d in expected_distances]}")
    actual_distances = [np.linalg.norm(engine._positions[i]) for i in source_ids]
    print(f"📏 Distancias actuales: {[f'{d:.2f}' for d in actual_distances]}")
else:
    print("\n❌ Las fuentes NO se movieron")
    print("\n🔍 Debug adicional:")
    
    # Ver estado del macro
    macro = engine._macros[macro_name]
    if hasattr(macro, 'concentration_active'):
        print(f"   concentration_active: {macro.concentration_active}")
    if hasattr(macro, 'concentration_progress'):
        print(f"   concentration_progress: {macro.concentration_progress}")