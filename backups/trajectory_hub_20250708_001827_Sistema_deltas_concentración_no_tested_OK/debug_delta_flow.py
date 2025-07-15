# === debug_delta_flow.py ===
# 🔧 Debug profundo del flujo de deltas
# ⚡ Rastrea exactamente dónde falla

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🔍 DEBUG PROFUNDO DEL FLUJO DE DELTAS")
print("="*60)

# Setup
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=1)  # Solo 1 fuente para simplificar

# Posición inicial
engine._positions[0] = np.array([10.0, 0.0, 0.0])
print(f"📍 Posición inicial: {engine._positions[0]}")

# Aplicar concentración
print("\n🎯 Aplicando concentración...")
engine.set_macro_concentration(macro, factor=0.5)

# Debug del componente
print("\n🔍 Verificando componente:")
motion = engine.motion_states[0]
print(f"   motion_states[0] existe: ✅")
print(f"   active_components: {motion.active_components}")

if isinstance(motion.active_components, dict):
    comp = motion.active_components.get('concentration')
    if comp:
        print(f"   ConcentrationComponent encontrado: ✅")
        print(f"   Factor: {comp.concentration_factor}")
        print(f"   Centro: {comp.center}")
        
        # Test calculate_delta directamente
        print("\n🧪 Test directo de calculate_delta:")
        state = motion.motion_state
        delta = comp.calculate_delta(state, 0.0, 0.016)
        print(f"   Delta: {delta}")
        if hasattr(delta, 'position'):
            print(f"   Delta.position: {delta.position}")
else:
    print(f"   active_components es lista con {len(motion.active_components)} elementos")

# Interceptar update_with_deltas
print("\n🔍 Interceptando update_with_deltas:")
original_update = motion.update_with_deltas

def debug_update_with_deltas(current_time, dt):
    print(f"\n   🎯 update_with_deltas llamado!")
    print(f"      current_time: {current_time}")
    print(f"      dt: {dt}")
    result = original_update(current_time, dt)
    print(f"      Resultado: {result}")
    print(f"      Tipo: {type(result)}")
    if isinstance(result, list):
        print(f"      Número de deltas: {len(result)}")
        for i, d in enumerate(result):
            print(f"      Delta {i}: {d}")
            if hasattr(d, 'position'):
                print(f"         position: {d.position}")
    return result

motion.update_with_deltas = debug_update_with_deltas

# Interceptar update del engine
print("\n🔍 Interceptando engine.update:")
original_engine_update = engine.update
update_called = [False]

def debug_engine_update():
    update_called[0] = True
    print("\n   🎯 engine.update() llamado!")
    
    # Verificar si el código de deltas se ejecuta
    if hasattr(engine, 'motion_states'):
        print("      motion_states existe ✅")
        print(f"      Número de estados: {len(engine.motion_states)}")
    
    # Posición antes
    pos_before = engine._positions[0].copy()
    
    # Llamar update original
    result = original_engine_update()
    
    # Posición después
    pos_after = engine._positions[0]
    diff = pos_after - pos_before
    print(f"      Cambio en posición: {diff}")
    
    return result

engine.update = debug_engine_update

# Ejecutar UN frame
print("\n🔄 Ejecutando UN frame de update:")
engine.update()

if not update_called[0]:
    print("\n❌ engine.update() NO fue llamado")

# Resultado final
print("\n📊 RESULTADO:")
print(f"   Posición final: {engine._positions[0]}")
print(f"   Distancia al centro: {np.linalg.norm(engine._positions[0]):.4f}")

# Debug adicional
print("\n🔍 Debug adicional:")
print(f"   engine.dt: {getattr(engine, 'dt', 'NO EXISTE')}")
print(f"   engine._time: {getattr(engine, '_time', 'NO EXISTE')}")