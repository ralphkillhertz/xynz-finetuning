# === test_delta_minimal_working.py ===
# 🔧 Test mínimo que FUNCIONA
# ⚡ Sin errores de parámetros

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 TEST MÍNIMO DE DELTAS")
print("="*60)

# 1. Crear engine
engine = EnhancedTrajectoryEngine()
print("✅ Engine creado")

# 2. Crear macro con parámetro correcto
source_ids = engine.create_macro("test", source_count=3)
print(f"✅ Macro creado: {source_ids}")

# 3. Posiciones iniciales
print("\n📍 Posiciones iniciales:")
for sid in source_ids:
    print(f"   Source {sid}: {engine._positions[sid]}")

# 4. Aplicar concentración
engine.apply_concentration("test", factor=0.8)
print("\n✅ Concentración aplicada (factor=0.8)")

# 5. Guardar posiciones
pos_before = {sid: engine._positions[sid].copy() for sid in source_ids}

# 6. Actualizar
print("\n🔄 Actualizando...")
if hasattr(engine, 'update'):
    engine.update(0.016)
    print("✅ engine.update(0.016) ejecutado")
elif hasattr(engine, 'step'):
    engine.step()
    print("✅ engine.step() ejecutado")

# 7. Verificar cambio
print("\n📊 Resultado:")
moved = False
for sid in source_ids:
    before = pos_before[sid]
    after = engine._positions[sid]
    diff = after - before
    if np.any(diff != 0):
        print(f"   Source {sid}: MOVIÓ {diff} ✅")
        moved = True
    else:
        print(f"   Source {sid}: NO se movió ❌")

if moved:
    print("\n🎉 ¡ÉXITO! Las fuentes se están moviendo")
else:
    print("\n❌ Las fuentes NO se mueven")
    
    # Debug rápido
    if hasattr(engine, 'motion_states'):
        motion = engine.motion_states.get(source_ids[0])
        if motion and hasattr(motion, 'active_components'):
            print(f"\n🔍 Componentes activos: {list(motion.active_components.keys())}")