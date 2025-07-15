#!/usr/bin/env python3
"""
test_concentration_simple.py - Test simple del sistema
"""

from trajectory_hub import EnhancedTrajectoryEngine

print("🧪 TEST SIMPLE DE CONCENTRACIÓN\n")

# Crear engine
engine = EnhancedTrajectoryEngine()
print("✅ Engine creado")

# Crear macro
macro_id = engine.create_macro("test", 5, formation="circle")
print(f"✅ Macro creado: {macro_id}")

# Establecer concentración
engine.set_macro_concentration(macro_id, 0.0)  # Totalmente concentrado
print("✅ Concentración establecida en 0.0")

# Updates
print("\nEjecutando updates...")
for i in range(10):
    engine.update()
    if i % 3 == 0:
        state = engine.get_macro_concentration_state(macro_id)
        print(f"  Frame {i}: factor={state.get('factor', 'N/A')}")

print("\n✅ TEST COMPLETADO SIN ERRORES")
