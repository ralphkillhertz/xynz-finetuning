# === test_delta_working_from_previous.py ===
# 🔧 Test basado en trabajo previo exitoso
# ⚡ Usando lo que YA sabemos que funciona

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 TEST DE DELTAS (versión probada)")
print("="*60)

# 1. Crear engine - sabemos que funciona sin parámetros
engine = EnhancedTrajectoryEngine()
print("✅ Engine creado")

# 2. Crear macro - sabemos que retorna el nombre
macro_name = engine.create_macro("test", source_count=3)
print(f"✅ Macro creado: {macro_name}")

# 3. Obtener IDs correctamente
source_ids = engine.macros[macro_name].source_ids
print(f"✅ Source IDs: {source_ids}")

# 4. Posiciones iniciales
print("\n📍 Posiciones iniciales:")
for sid in source_ids:
    pos = engine._positions[sid]
    print(f"   Source {sid}: {pos}")

# 5. Aplicar concentración
engine.apply_concentration(macro_name, factor=0.8)
print("\n✅ Concentración aplicada (factor=0.8)")

# 6. Verificar que el componente existe
motion = engine.motion_states[source_ids[0]]
if hasattr(motion, 'active_components'):
    comp = motion.active_components.get('concentration')
    if comp:
        print(f"✅ ConcentrationComponent encontrado")
        print(f"   Factor: {comp.concentration_factor}")
        
        # Sabemos que calculate_delta funciona
        state = motion.motion_state
        delta = comp.calculate_delta(state, 0.0, 0.016)
        if hasattr(delta, 'position'):
            print(f"   ✅ Delta calculado: {delta.position}")

# 7. Guardar posiciones
pos_before = {}
for sid in source_ids:
    pos_before[sid] = engine._positions[sid].copy()

# 8. Actualizar
print("\n🔄 Actualizando...")
engine.update(0.016)

# 9. Verificar cambio
print("\n📊 Resultado:")
any_movement = False
for sid in source_ids:
    before = pos_before[sid]
    after = engine._positions[sid]
    diff = after - before
    distance = np.linalg.norm(diff)
    
    if distance > 0.0001:
        print(f"   Source {sid}: MOVIÓ {distance:.4f} unidades ✅")
        print(f"      Cambio: {diff}")
        any_movement = True
    else:
        print(f"   Source {sid}: NO se movió ❌")

if any_movement:
    print("\n🎉 ¡ÉXITO! El sistema de deltas funciona")
else:
    print("\n❌ Las fuentes NO se mueven")
    print("\n🔍 Problema conocido: Los deltas se calculan pero no se aplican")
    print("   Delta esperado: [-0.8, 0., 0.] por fuente")
    print("   Siguiente paso: Verificar engine.update()")