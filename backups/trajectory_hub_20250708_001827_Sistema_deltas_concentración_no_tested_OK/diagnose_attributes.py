# === diagnose_attributes.py ===
# 🔧 Diagnóstico de atributos reales
# ⚡ Sin asumir nombres de atributos

import numpy as np
from trajectory_hub import EnhancedTrajectoryEngine

print("🔍 DIAGNÓSTICO DE ATRIBUTOS REALES")
print("="*60)

# Setup
engine = EnhancedTrajectoryEngine()
macro = engine.create_macro("test", source_count=1)
engine._positions[0] = np.array([10.0, 0.0, 0.0])

# Concentración
engine.set_macro_concentration(macro, factor=0.5)

# Explorar estructura
motion = engine.motion_states[0]
print("\n1️⃣ Atributos de SourceMotion:")
attrs = [a for a in dir(motion) if not a.startswith('_')]
for attr in sorted(attrs):
    value = getattr(motion, attr)
    if not callable(value):
        print(f"   {attr}: {type(value).__name__}")

# Explorar componente
print("\n2️⃣ Componente de concentración:")
if motion.active_components and len(motion.active_components) > 0:
    comp = motion.active_components[0]
    print(f"   Tipo: {type(comp).__name__}")
    
    comp_attrs = [a for a in dir(comp) if not a.startswith('_')]
    for attr in sorted(comp_attrs):
        value = getattr(comp, attr)
        if not callable(value):
            print(f"   {attr}: {value}")

# Test calculate_delta con diferentes opciones
print("\n3️⃣ Test de calculate_delta:")
if hasattr(comp, 'calculate_delta'):
    # Probar diferentes atributos para state
    state_options = ['state', 'motion_state', motion]
    
    for state_opt in state_options:
        if isinstance(state_opt, str):
            if hasattr(motion, state_opt):
                state = getattr(motion, state_opt)
                print(f"\n   Probando con motion.{state_opt}:")
            else:
                continue
        else:
            state = state_opt
            print(f"\n   Probando con motion directamente:")
        
        try:
            delta = comp.calculate_delta(state, 0.0, 0.016)
            print(f"   ✅ Funcionó! Delta: {delta}")
            if hasattr(delta, 'position'):
                print(f"   Delta.position: {delta.position}")
            break
        except Exception as e:
            print(f"   ❌ Error: {e}")

# Test manual de concentración
print("\n4️⃣ Cálculo manual de concentración:")
if hasattr(comp, 'center') and hasattr(comp, 'concentration_factor'):
    print(f"   Centro: {comp.center}")
    print(f"   Factor: {comp.concentration_factor}")
    print(f"   Posición actual: {engine._positions[0]}")
    
    # Cálculo manual
    direction = comp.center - engine._positions[0]
    movement = direction * comp.concentration_factor * 0.016
    print(f"   Movimiento esperado: {movement}")