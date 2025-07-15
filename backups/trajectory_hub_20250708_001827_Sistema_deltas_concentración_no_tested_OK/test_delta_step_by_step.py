# === test_delta_step_by_step.py ===
# 🔧 Test paso a paso sin asumir estructura
# ⚡ Debug completo

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 TEST PASO A PASO")
print("="*60)

# 1. Crear engine
engine = EnhancedTrajectoryEngine()
print("✅ Engine creado")

# 2. Crear macro
macro_name = engine.create_macro("test", source_count=3)
print(f"✅ Macro: {macro_name}")

# 3. Explorar _macros
print("\n🔍 Explorando _macros:")
if hasattr(engine, '_macros'):
    macro = engine._macros[macro_name]
    print(f"   Tipo: {type(macro)}")
    print(f"   Atributos: {[a for a in dir(macro) if not a.startswith('_')][:10]}")
    
    # Source IDs
    if hasattr(macro, 'source_ids'):
        source_ids = list(macro.source_ids)
        print(f"   source_ids: {source_ids}")

# 4. Ver motion_states
print("\n🔍 Explorando motion_states:")
if hasattr(engine, 'motion_states'):
    states = engine.motion_states
    print(f"   Tipo: {type(states)}")
    print(f"   Keys: {list(states.keys())}")
    
    # Ver estructura del primer estado
    if 0 in states:
        state0 = states[0]
        print(f"\n   motion_states[0]:")
        print(f"     Tipo: {type(state0)}")
        print(f"     Atributos: {[a for a in dir(state0) if not a.startswith('_')][:10]}")
        
        # active_components
        if hasattr(state0, 'active_components'):
            comps = state0.active_components
            print(f"     active_components tipo: {type(comps)}")
            if isinstance(comps, dict):
                print(f"     active_components keys: {list(comps.keys())}")
            elif isinstance(comps, list):
                print(f"     active_components length: {len(comps)}")

# 5. Probar apply_concentration con diferentes sintaxis
print("\n🧪 Probando apply_concentration:")

# Intentar diferentes formas
attempts = [
    ("apply_concentration(macro_name, 0.8)", 
     lambda: engine.apply_concentration(macro_name, 0.8)),
    ("apply_concentration(macro_name, concentration_factor=0.8)", 
     lambda: engine.apply_concentration(macro_name, concentration_factor=0.8)),
    ("apply_concentration(macro_name)", 
     lambda: engine.apply_concentration(macro_name)),
]

for desc, func in attempts:
    try:
        func()
        print(f"   ✅ {desc} funcionó")
        break
    except Exception as e:
        print(f"   ❌ {desc}: {type(e).__name__}: {e}")

# 6. Ver si las posiciones cambiaron
print("\n📍 Posiciones después de crear macro:")
for i in range(3):
    pos = engine._positions[i]
    print(f"   Source {i}: {pos}")

# 7. Si las posiciones son [0,0,0], intentar set_macro_formation
if np.all(engine._positions[:3] == 0):
    print("\n⚠️ Posiciones en cero, intentando set_macro_formation...")
    if hasattr(engine, 'set_macro_formation'):
        try:
            engine.set_macro_formation(macro_name, "circle", radius=10.0)
            print("✅ Formation aplicada")
            # Ver nuevas posiciones
            print("\n📍 Nuevas posiciones:")
            for i in range(3):
                pos = engine._positions[i]
                print(f"   Source {i}: {pos}")
        except Exception as e:
            print(f"❌ Error: {e}")