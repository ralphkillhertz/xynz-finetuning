# === test_concentration_direct.py ===
# 🔧 Test directo del sistema de concentración REAL
# ⚡ Sin asumir sistema de deltas

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 TEST DIRECTO DE CONCENTRACIÓN")
print("="*60)

# 1. Setup básico
engine = EnhancedTrajectoryEngine()
macro_name = engine.create_macro("test", source_count=3)
source_ids = [0, 1, 2]

# 2. Posiciones iniciales
print("\n📍 Estableciendo posiciones iniciales...")
positions = [
    [10, 0, 0],
    [-5, 8.66, 0],
    [-5, -8.66, 0]
]
for i, pos in enumerate(positions):
    engine._positions[i] = np.array(pos, dtype=float)
    print(f"   Source {i}: {engine._positions[i]}")

# 3. Aplicar concentración
print("\n🎯 Aplicando concentración...")
center = np.array([0, 0, 0])
engine.apply_concentration(macro_name, center)
print("✅ Concentración aplicada")

# 4. Ver estado del macro
print("\n🔍 Estado del macro:")
macro = engine._macros[macro_name]
attrs_to_check = ['concentration_active', 'concentration_factor', 'concentration_center', 
                  'concentration_duration', 'concentration_target']
for attr in attrs_to_check:
    if hasattr(macro, attr):
        value = getattr(macro, attr)
        print(f"   {attr}: {value}")

# 5. Guardar posiciones
pos_before = {i: engine._positions[i].copy() for i in source_ids}

# 6. Actualizar varias veces
print("\n🔄 Actualizando 10 frames...")
for frame in range(10):
    engine.update()  # Sin parámetros
    
    # Verificar movimiento cada 5 frames
    if frame % 5 == 4:
        print(f"\n   Frame {frame+1}:")
        for i in source_ids:
            dist = np.linalg.norm(engine._positions[i] - pos_before[i])
            if dist > 0.001:
                print(f"     Source {i}: movió {dist:.4f} ✅")
            else:
                print(f"     Source {i}: no movió ❌")

# 7. Resultado final
print("\n📊 RESULTADO FINAL:")
for i in source_ids:
    before = pos_before[i]
    after = engine._positions[i]
    dist = np.linalg.norm(after - before)
    
    print(f"\n   Source {i}:")
    print(f"     Inicial: {before}")
    print(f"     Final:   {after}")
    print(f"     Distancia: {dist:.4f}")
    
    if dist > 0.001:
        print("     ✅ SE MOVIÓ")
    else:
        print("     ❌ NO SE MOVIÓ")

# 8. Probar animate_macro_concentration
print("\n🎬 Probando animate_macro_concentration...")
if hasattr(engine, 'animate_macro_concentration'):
    try:
        result = engine.animate_macro_concentration(macro_name)
        print(f"   Resultado: {result}")
        
        # Actualizar más frames
        print("\n🔄 Actualizando 10 frames más...")
        for _ in range(10):
            engine.update()
            
        # Ver movimiento final
        print("\n📊 Después de animate:")
        for i in source_ids:
            final = engine._positions[i]
            total_dist = np.linalg.norm(final - pos_before[i])
            print(f"   Source {i}: distancia total = {total_dist:.4f}")
            
    except Exception as e:
        print(f"   Error: {e}")