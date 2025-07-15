# === test_delta_real_structure.py ===
# 🔧 Test con la estructura REAL descubierta
# ⚡ Sin asumir nada del trabajo anterior

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 TEST CON ESTRUCTURA REAL")
print("="*60)

# 1. Crear engine y macro
engine = EnhancedTrajectoryEngine()
macro_name = engine.create_macro("test", source_count=3)
source_ids = [0, 1, 2]
print(f"✅ Macro creado: {macro_name}")

# 2. Establecer posiciones iniciales (no cero)
print("\n📍 Estableciendo posiciones iniciales...")
# Círculo de radio 10
angles = np.linspace(0, 2*np.pi, 4)[:-1]  # 3 puntos
for i, sid in enumerate(source_ids):
    x = 10 * np.cos(angles[i])
    y = 10 * np.sin(angles[i])
    engine._positions[sid] = np.array([x, y, 0])
    print(f"   Source {sid}: {engine._positions[sid]}")

# 3. Calcular centro del macro
center = np.mean([engine._positions[sid] for sid in source_ids], axis=0)
print(f"\n📊 Centro del macro: {center}")

# 4. Aplicar concentración con punto
print("\n🎯 Aplicando concentración hacia el centro...")
try:
    # apply_concentration espera (macro_name, point)
    engine.apply_concentration(macro_name, center)
    print("✅ Concentración aplicada")
except Exception as e:
    print(f"❌ Error: {e}")
    # Intentar con [0,0,0]
    try:
        engine.apply_concentration(macro_name, np.array([0, 0, 0]))
        print("✅ Concentración aplicada hacia [0,0,0]")
    except Exception as e2:
        print(f"❌ Error con [0,0,0]: {e2}")

# 5. Verificar componentes (sabiendo que es lista)
print("\n🔍 Verificando componentes:")
for sid in source_ids:
    motion = engine.motion_states[sid]
    comps = motion.active_components
    print(f"   Source {sid}:")
    print(f"     active_components: {comps}")
    print(f"     Número de componentes: {len(comps)}")
    
    # Si hay componentes, explorar
    if len(comps) > 0:
        for i, comp in enumerate(comps):
            print(f"     Componente {i}: {type(comp).__name__}")
            if hasattr(comp, 'enabled'):
                print(f"       - enabled: {comp.enabled}")

# 6. Guardar posiciones
pos_before = {sid: engine._positions[sid].copy() for sid in source_ids}

# 7. Actualizar
print("\n🔄 Actualizando...")
for i in range(5):  # 5 frames
    engine.update(0.016)
print("✅ 5 frames actualizados")

# 8. Verificar cambios
print("\n📊 Resultado:")
total_movement = 0
for sid in source_ids:
    before = pos_before[sid]
    after = engine._positions[sid]
    diff = after - before
    dist = np.linalg.norm(diff)
    total_movement += dist
    
    if dist > 0.001:
        print(f"   Source {sid}: MOVIÓ {dist:.4f} ✅")
        print(f"      De: {before}")
        print(f"      A:  {after}")
    else:
        print(f"   Source {sid}: NO movió ❌")

if total_movement > 0.001:
    print(f"\n🎉 ¡ÉXITO! Movimiento total: {total_movement:.4f}")
else:
    print("\n❌ Sin movimiento")
    
    # Debug adicional
    print("\n🔍 Debug adicional:")
    # Ver si hay método para activar concentración
    if hasattr(engine, 'animate_macro_concentration'):
        print("   ✅ Encontrado: animate_macro_concentration")
        print("      Intentando activar...")
        try:
            engine.animate_macro_concentration(macro_name)
            print("      ✅ Activado")
        except Exception as e:
            print(f"      ❌ Error: {e}")