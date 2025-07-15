# === debug_concentration_attributes.py ===
# 🔧 Debug completo de atributos
# ⚡ Qué tiene realmente ConcentrationComponent

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🔍 DEBUG COMPLETO DE ATRIBUTOS")
print("="*60)

# Setup
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=1)
engine._positions[0] = np.array([10.0, 0.0, 0.0])

# Aplicar concentración
engine.set_macro_concentration(macro, factor=0.5)

# Explorar
motion = engine.motion_states[0]
comp = motion.active_components[0]

print("\n📋 Atributos de ConcentrationComponent:")
attrs = [a for a in dir(comp) if not a.startswith('_')]
for attr in sorted(attrs):
    try:
        value = getattr(comp, attr)
        if not callable(value):
            print(f"   {attr}: {value}")
    except:
        print(f"   {attr}: [ERROR al leer]")

# Test calculate_delta con información completa
print("\n🧪 Test de calculate_delta:")
state = motion.state
print(f"   state.position: {state.position}")
print(f"   state.source_id: {state.source_id}")

# Llamar calculate_delta
try:
    delta = comp.calculate_delta(state, 0, 0.016)
    print(f"   Delta: {delta}")
    if hasattr(delta, 'position'):
        print(f"   Delta.position: {delta.position}")
        
        # Si es [0,0,0], debug por qué
        if all(v == 0 for v in delta.position):
            print("\n❌ Delta es [0,0,0]")
            
            # Verificar el centro usado
            if hasattr(comp, 'macro_center'):
                print(f"   macro_center: {comp.macro_center}")
            if hasattr(comp, 'target_point'):
                print(f"   target_point: {comp.target_point}")
            
            # El problema puede ser que el centro es igual a la posición
            print(f"\n🔍 Comparando posiciones:")
            print(f"   state.position: {state.position}")
            print(f"   engine._positions[0]: {engine._positions[0]}")
            
            # Si son diferentes, ese es el problema
            if not np.array_equal(state.position, engine._positions[0]):
                print("\n❌ PROBLEMA: state.position no coincide con engine._positions")
                print("   Necesitamos sincronizar estas posiciones")
except Exception as e:
    print(f"   Error en calculate_delta: {e}")
    import traceback
    traceback.print_exc()

# Solución propuesta
print("\n🔧 SOLUCIÓN PROPUESTA:")
print("   El problema es que ConcentrationComponent calcula el delta")
print("   basándose en state.position, pero este no se actualiza")
print("   cuando cambia engine._positions")
print("\n   Necesitamos:")
print("   1. Sincronizar state.position con engine._positions")
print("   2. O modificar calculate_delta para usar engine._positions")