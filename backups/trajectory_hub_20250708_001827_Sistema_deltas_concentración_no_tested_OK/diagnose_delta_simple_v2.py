# === diagnose_delta_simple_v2.py ===
# 🔧 Diagnóstico simple y directo v2
# ⚡ Sin nonlocal, más simple

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent

print("🔍 DIAGNÓSTICO SIMPLE DE DELTAS V2")
print("="*60)

# Setup
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=1)
engine._positions[0] = np.array([10.0, 0.0, 0.0])

print("1️⃣ Estado inicial:")
print(f"   Posición: {engine._positions[0]}")

# Aplicar concentración
print("\n2️⃣ Aplicando concentración...")
engine.set_macro_concentration(macro, factor=0.5)

# Verificar componente
motion = engine.motion_states[0]
print("\n3️⃣ Verificando componente:")
print(f"   active_components: {motion.active_components}")
print(f"   Tipo: {type(motion.active_components)}")

if isinstance(motion.active_components, list) and len(motion.active_components) > 0:
    comp = motion.active_components[0]
    print(f"   Componente: {type(comp).__name__}")
    
    if hasattr(comp, 'calculate_delta'):
        print("\n4️⃣ Test manual de calculate_delta:")
        state = motion.motion_state
        delta = comp.calculate_delta(state, 0.0, 0.016)
        print(f"   Delta: {delta}")
        
        if hasattr(delta, 'position'):
            print(f"   Delta.position: {delta.position}")
            expected_movement = delta.position
            print(f"   Movimiento esperado: {expected_movement}")

# Test update_with_deltas
print("\n5️⃣ Test de update_with_deltas:")
if hasattr(motion, 'update_with_deltas'):
    deltas = motion.update_with_deltas(0.0, 0.016)
    print(f"   ✅ Método existe")
    print(f"   Retorna: {deltas}")
    print(f"   Es lista: {isinstance(deltas, list)}")
    if isinstance(deltas, list):
        print(f"   Número de deltas: {len(deltas)}")
else:
    print("   ❌ Método NO existe")
    
    # Intentar añadirlo dinámicamente para test
    print("\n   🔧 Añadiendo update_with_deltas dinámicamente...")
    
    def temp_update_with_deltas(self, current_time, dt):
        deltas = []
        for comp in self.active_components:
            if hasattr(comp, 'calculate_delta') and hasattr(comp, 'enabled') and comp.enabled:
                delta = comp.calculate_delta(self.motion_state, current_time, dt)
                if delta:
                    deltas.append(delta)
        return deltas
    
    import types
    motion.update_with_deltas = types.MethodType(temp_update_with_deltas, motion)
    print("   ✅ Método añadido temporalmente")

# Guardar posición
pos_before = engine._positions[0].copy()

# Update manual
print("\n6️⃣ Ejecutando engine.update()...")
engine.update()

# Verificar cambio
pos_after = engine._positions[0]
change = pos_after - pos_before
distance_moved = np.linalg.norm(change)

print(f"\n📊 RESULTADO:")
print(f"   Posición antes: {pos_before}")
print(f"   Posición después: {pos_after}")
print(f"   Cambio: {change}")
print(f"   Distancia movida: {distance_moved:.6f}")

if distance_moved > 0.0001:
    print("\n🎉 ¡LAS FUENTES SE MUEVEN!")
else:
    print("\n❌ Las fuentes NO se mueven")
    
    # Debug adicional
    print("\n🔍 Debug adicional:")
    
    # Verificar si el código de deltas está en update
    import inspect
    try:
        source = inspect.getsource(engine.update)
        has_delta_code = 'PROCESAMIENTO DE DELTAS' in source
        has_motion_loop = 'for source_id, motion in self.motion_states.items()' in source
        has_position_update = '_positions[source_id] +=' in source
        
        print(f"   Código de deltas presente: {'✅' if has_delta_code else '❌'}")
        print(f"   Loop de motion_states: {'✅' if has_motion_loop else '❌'}")
        print(f"   Actualización de posiciones: {'✅' if has_position_update else '❌'}")
        
        if not has_delta_code:
            print("\n   ⚠️ El código de deltas NO está en update()")
            print("   Necesitas ejecutar fix_update_deltas_precise.py")
    except:
        pass