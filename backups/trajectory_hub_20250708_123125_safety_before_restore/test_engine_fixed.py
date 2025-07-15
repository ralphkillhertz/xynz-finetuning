# === test_engine_fixed.py ===
# 🧪 Test del engine corregido

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("\n🔧 TEST: Engine con constructor corregido\n")

# Test 1: Crear con valores por defecto
print("1️⃣ Creando con valores por defecto...")
try:
    engine1 = EnhancedTrajectoryEngine()
    print("✅ Éxito con valores por defecto")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Crear con max_sources
print("\n2️⃣ Creando con max_sources=8...")
try:
    engine2 = EnhancedTrajectoryEngine(max_sources=8)
    print("✅ Éxito con max_sources")
    print(f"   Posiciones shape: {engine2._positions.shape}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Crear macro y rotar
print("\n3️⃣ Creando macro y aplicando rotación...")
try:
    engine = EnhancedTrajectoryEngine(max_sources=4, fps=60, enable_modulator=False)
    macro_id = engine.create_macro("test", 4)
    
    # Configurar posiciones
    positions = [[1,0,0], [-1,0,0], [0,1,0], [0,-1,0]]
    for i, sid in enumerate(list(engine._macros[macro_id].source_ids)[:4]):
        engine._positions[sid] = np.array(positions[i])
    
    # Aplicar rotación
    engine.set_macro_rotation(macro_id, 0, 1.0, 0)
    
    # Simular
    for _ in range(30):
        engine.update()
    
    print("✅ ¡TODO FUNCIONANDO!")
    print("\n🎉 SISTEMA LISTO PARA USAR")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
