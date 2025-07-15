# === diagnose_complete_delta_flow.py ===
# 🔧 Diagnóstico COMPLETO del sistema de deltas
# ⚡ Rastrea TODO el flujo paso a paso

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import ConcentrationComponent, MotionDelta

print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA DE DELTAS")
print("="*60)

# 1. Setup básico
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=1)
engine._positions[0] = np.array([10.0, 0.0, 0.0])

print("1️⃣ Setup inicial:")
print(f"   Posición: {engine._positions[0]}")
print(f"   motion_states keys: {list(engine.motion_states.keys())}")

# 2. Aplicar concentración
print("\n2️⃣ Aplicando concentración...")
engine.set_macro_concentration(macro, factor=0.5)

# 3. Verificar componente
print("\n3️⃣ Verificando ConcentrationComponent:")
motion = engine.motion_states[0]
print(f"   motion tipo: {type(motion)}")
print(f"   active_components tipo: {type(motion.active_components)}")

if isinstance(motion.active_components, list):
    print(f"   Número de componentes: {len(motion.active_components)}")
    if len(motion.active_components) > 0:
        comp = motion.active_components[0]
        print(f"   Componente 0: {type(comp).__name__}")
        
        if isinstance(comp, ConcentrationComponent):
            print(f"   ✅ Es ConcentrationComponent")
            print(f"   enabled: {comp.enabled}")
            print(f"   factor: {comp.concentration_factor}")
            print(f"   center: {comp.center}")
            
            # 4. Test directo de calculate_delta
            print("\n4️⃣ Test directo de calculate_delta:")
            state = motion.motion_state
            print(f"   motion_state.position: {state.position}")
            
            # Llamar calculate_delta manualmente
            delta = comp.calculate_delta(state, 0.0, 0.016)
            print(f"   Delta retornado: {delta}")
            
            if delta:
                print(f"   Delta tipo: {type(delta)}")
                if hasattr(delta, 'position'):
                    print(f"   Delta.position: {delta.position}")
                    print(f"   ✅ calculate_delta funciona!")

# 5. Test update_with_deltas
print("\n5️⃣ Test de update_with_deltas:")
if hasattr(motion, 'update_with_deltas'):
    print("   ✅ update_with_deltas existe")
    
    # Llamar manualmente
    deltas = motion.update_with_deltas(0.0, 0.016)
    print(f"   Deltas retornados: {deltas}")
    print(f"   Tipo: {type(deltas)}")
    print(f"   Número de deltas: {len(deltas) if isinstance(deltas, list) else 'No es lista'}")
else:
    print("   ❌ update_with_deltas NO existe")

# 6. Verificar si update llama a update_with_deltas
print("\n6️⃣ Verificando si engine.update procesa deltas:")

# Interceptar _positions para ver cambios
original_positions = engine._positions.copy()
positions_changed = False

class PositionMonitor:
    def __setitem__(self, key, value):
        nonlocal positions_changed
        if not np.array_equal(original_positions[key], value):
            positions_changed = True
            print(f"\n   🎯 CAMBIO DETECTADO en posición {key}!")
            print(f"      De: {original_positions[key]}")
            print(f"      A:  {value}")
        original_positions[key] = value
    
    def __getitem__(self, key):
        return original_positions[key]
    
    def __getattr__(self, name):
        return getattr(original_positions, name)

# Reemplazar temporalmente
engine._positions = PositionMonitor()

# Ejecutar update
print("\n7️⃣ Ejecutando engine.update()...")
engine.update()

if not positions_changed:
    print("   ❌ Las posiciones NO cambiaron")
    
    # Verificar el código de update
    print("\n8️⃣ Verificando código de engine.update:")
    import inspect
    try:
        source = inspect.getsource(engine.update)
        if 'PROCESAMIENTO DE DELTAS' in source:
            print("   ✅ Código de deltas está presente")
            
            # Buscar líneas clave
            lines = source.split('\n')
            for i, line in enumerate(lines):
                if 'motion_states' in line and 'for' in line:
                    print(f"   Línea {i}: {line.strip()}")
                if 'update_with_deltas' in line:
                    print(f"   Línea {i}: {line.strip()}")
                if '_positions[source_id] +=' in line:
                    print(f"   Línea {i}: {line.strip()}")
        else:
            print("   ❌ Código de deltas NO está presente")
    except:
        print("   ❌ No se pudo obtener el código fuente")

# Restaurar positions
engine._positions = original_positions

print("\n📊 RESUMEN DEL DIAGNÓSTICO:")
print("   1. ConcentrationComponent existe: ✅" if len(motion.active_components) > 0 else "   1. ConcentrationComponent existe: ❌")
print("   2. calculate_delta funciona: ✅" if 'delta' in locals() else "   2. calculate_delta funciona: ❌")
print("   3. update_with_deltas existe: ✅" if hasattr(motion, 'update_with_deltas') else "   3. update_with_deltas existe: ❌")
print("   4. engine.update procesa deltas: ✅" if positions_changed else "   4. engine.update procesa deltas: ❌")