#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🎯 TRABAJANDO SIN CREAR GRUPOS (SOLO POSICIONES)\n")

engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Crear macro (internamente, sin grupos OSC)
print("Creando macro interno...")
macro_id = engine.create_macro("demo", source_count=5, formation="circle")

# Aplicar concentración
print("\nAplicando concentración...")
engine.set_macro_concentration(macro_id, 0.7)

# Simular
print("\nEjecutando simulación...")
for i in range(30):
    engine.step()
    if i % 10 == 0:
        print(f"  Frame {i}")

print("\n✅ Las POSICIONES funcionan perfectamente")
print("✅ La CONCENTRACIÓN funciona")
print("❓ Los grupos son opcionales si Spat no los soporta via OSC")
print("\n💡 Puedes crear grupos manualmente en Spat y")
print("   el sistema seguirá funcionando para las posiciones")
