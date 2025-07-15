# === test_delta_correct_structure.py ===
# 🔧 Test usando la estructura REAL encontrada
# ⚡ Basado en la exploración exitosa

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 TEST DE DELTAS - ESTRUCTURA CORRECTA")
print("="*60)

# 1. Crear engine
engine = EnhancedTrajectoryEngine()
print("✅ Engine creado")

# 2. Crear macro
macro_name = engine.create_macro("test", source_count=3)
print(f"✅ Macro creado: {macro_name}")

# 3. Los IDs son simplemente 0, 1, 2
source_ids = [0, 1, 2]
print(f"✅ Source IDs: {source_ids}")

# 4. Verificar macro en _macros
if hasattr(engine, '_macros'):
    macro = engine._macros.get(macro_name)
    if macro:
        print(f"✅ Macro encontrado en _macros")
        if hasattr(macro, 'source_ids'):
            print(f"   source_ids del macro: {macro.source_ids}")
            source_ids = macro.source_ids

# 5. Posiciones iniciales
print("\n📍 Posiciones iniciales:")
for sid in source_ids:
    pos = engine._positions[sid]
    print(f"   Source {sid}: {pos}")

# 6. Aplicar concentración (sin keyword 'factor')
print("\n🎯 Aplicando concentración...")
try:
    engine.apply_concentration(macro_name, 0.8)  # Sin keyword
    print("✅ Concentración aplicada")
except Exception as e:
    print(f"❌ Error: {e}")
    # Intentar otras formas
    try:
        engine.apply_concentration(macro_name, concentration_factor=0.8)
        print("✅ Concentración aplicada con concentration_factor")
    except:
        pass

# 7. Verificar componentes
print("\n🔍 Verificando componentes:")
if hasattr(engine, 'motion_states'):
    for sid in source_ids:
        motion = engine.motion_states.get(sid)
        if motion and hasattr(motion, 'active_components'):
            comps = motion.active_components
            print(f"   Source {sid}: {list(comps.keys())}")
            
            # Verificar concentración
            if 'concentration' in comps:
                comp = comps['concentration']
                print(f"     ✅ ConcentrationComponent encontrado")
                if hasattr(comp, 'concentration_factor'):
                    print(f"     Factor: {comp.concentration_factor}")

# 8. Guardar posiciones
pos_before = {}
for sid in source_ids:
    pos_before[sid] = engine._positions[sid].copy()

# 9. Actualizar usando ambos métodos
print("\n🔄 Actualizando...")
try:
    engine.update(0.016)
    print("✅ engine.update(0.016) ejecutado")
except Exception as e:
    print(f"❌ Error en update: {e}")

# También probar step
try:
    engine.step()
    print("✅ engine.step() ejecutado")
except Exception as e:
    print(f"❌ Error en step: {e}")

# 10. Verificar cambios
print("\n📊 Resultado:")
total_movement = 0
for sid in source_ids:
    before = pos_before[sid]
    after = engine._positions[sid]
    diff = after - before
    distance = np.linalg.norm(diff)
    total_movement += distance
    
    if distance > 0.0001:
        print(f"   Source {sid}: MOVIÓ {distance:.4f} unidades ✅")
        print(f"      De: {before}")
        print(f"      A:  {after}")
    else:
        print(f"   Source {sid}: NO se movió ❌")

if total_movement > 0.0001:
    print(f"\n🎉 ¡ÉXITO! Movimiento total: {total_movement:.4f}")
else:
    print("\n❌ Las fuentes NO se mueven")