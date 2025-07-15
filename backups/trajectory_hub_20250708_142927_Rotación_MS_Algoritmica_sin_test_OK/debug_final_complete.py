# === debug_final_complete.py ===
# 🔧 Debug COMPLETO del flujo
# ⚡ Rastreemos TODO el flujo paso a paso

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🔍 DEBUG FINAL COMPLETO")
print("="*60)

# Setup mínimo
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=1)
engine._positions[0] = np.array([10.0, 0.0, 0.0])

print(f"1️⃣ Posición inicial: {engine._positions[0]}")

# Aplicar concentración
engine.set_macro_concentration(macro, factor=0.5)

# Obtener referencias
motion = engine.motion_states[0]
comp = motion.active_components[0]

print(f"\n2️⃣ ConcentrationComponent creado:")
print(f"   Factor: {comp.concentration_factor}")
print(f"   Target: {comp.target_point}")

# Interceptar calculate_delta
original_calc = comp.calculate_delta
calc_called = [False]

def debug_calculate_delta(state, current_time, dt):
    calc_called[0] = True
    print(f"\n   🎯 calculate_delta LLAMADO!")
    print(f"      state.position: {state.position}")
    print(f"      target_point: {comp.target_point}")
    result = original_calc(state, current_time, dt)
    print(f"      Delta retornado: {result}")
    if hasattr(result, 'position'):
        print(f"      Delta.position: {result.position}")
    return result

comp.calculate_delta = debug_calculate_delta

# Interceptar update_with_deltas
if hasattr(motion, 'update_with_deltas'):
    original_update_deltas = motion.update_with_deltas
    update_deltas_called = [False]
    
    def debug_update_with_deltas(current_time, dt):
        update_deltas_called[0] = True
        print(f"\n   🎯 update_with_deltas LLAMADO!")
        result = original_update_deltas(current_time, dt)
        print(f"      Deltas retornados: {result}")
        return result
    
    motion.update_with_deltas = debug_update_with_deltas

# Interceptar el procesamiento en engine.update
print(f"\n3️⃣ Ejecutando engine.update()...")

# Guardar posición antes
pos_before = engine._positions[0].copy()

# Ejecutar update
engine.update()

# Verificar cambio
pos_after = engine._positions[0]
change = pos_after - pos_before

print(f"\n4️⃣ RESULTADO:")
print(f"   Posición antes: {pos_before}")
print(f"   Posición después: {pos_after}")
print(f"   Cambio: {change}")
print(f"   ¿Se movió?: {'✅ SÍ' if np.any(change != 0) else '❌ NO'}")

print(f"\n5️⃣ VERIFICACIÓN DE LLAMADAS:")
print(f"   calculate_delta fue llamado: {'✅' if calc_called[0] else '❌'}")
print(f"   update_with_deltas fue llamado: {'✅' if update_deltas_called[0] else '❌'}")

if not calc_called[0]:
    print("\n❌ PROBLEMA: calculate_delta NUNCA fue llamado")
    print("   El flujo se rompe antes de llegar ahí")
    
    # Test manual
    print("\n6️⃣ Test manual del flujo:")
    print("   Sincronizando state.position...")
    motion.state.position = engine._positions[0].copy()
    print(f"   state.position = {motion.state.position}")
    
    print("\n   Llamando update_with_deltas manualmente...")
    deltas = motion.update_with_deltas(0, 0.016)
    print(f"   Deltas: {deltas}")
    
    if deltas:
        print("\n   Aplicando deltas manualmente...")
        for delta in deltas:
            if hasattr(delta, 'position'):
                engine._positions[0] += delta.position
                print(f"   Nueva posición: {engine._positions[0]}")