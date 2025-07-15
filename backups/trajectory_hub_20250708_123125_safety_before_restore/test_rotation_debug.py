# === test_rotation_debug.py ===
# 🧪 Test debug de rotación MS

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np

print("\n🔍 DEBUG: Rotación MS\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=8, fps=60)

# Crear macro
macro_id = engine.create_macro("test", 4)

# Posiciones manuales en cuadrado
positions = [[1,0,0], [-1,0,0], [0,1,0], [0,-1,0]]
for i, sid in enumerate(list(engine._macros[macro_id].source_ids)[:4]):
    if sid < len(engine._positions):
        engine._positions[sid] = np.array(positions[i])
        if sid in engine.motion_states:
            engine.motion_states[sid].position = engine._positions[sid].copy()

print("📍 Posiciones iniciales:")
for sid in list(engine._macros[macro_id].source_ids)[:4]:
    if sid < len(engine._positions):
        p = engine._positions[sid]
        print(f"   Fuente {sid}: {p}")

# Intentar configurar rotación
print("\n🎯 Configurando rotación...")
try:
    # Verificar que el método existe
    if hasattr(engine, 'set_macro_rotation'):
        print("✅ Método existe")
        # Probar llamada
        engine.set_macro_rotation(macro_id, 0, 1.0, 0)
        print("✅ Rotación configurada")
    else:
        print("❌ Método no existe")
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Intentar sin keywords
    try:
        engine.set_macro_rotation(macro_id, 0, 1.0, 0)
        print("✅ Funciona sin keywords")
    except Exception as e2:
        print(f"❌ También falla sin keywords: {e2}")
