#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# NO deshabilitar OSC
if 'DISABLE_OSC' in os.environ:
    del os.environ['DISABLE_OSC']

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🧪 TEST ENGINE CON OSC\n")

# Crear engine (esto debe crear grupos en Spat)
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)

print("\nCreando macro con 3 fuentes...")
macro_id = engine.create_macro("demo", source_count=3, formation="triangle")

print("\nAplicando concentración...")
engine.set_macro_concentration(macro_id, 0.5)

print("\n🔄 Ejecutando algunos frames...")
for _ in range(5):
    engine.step()

print("\n✅ VERIFICA EN SPAT:")
print("   1. OSC Monitor debe mostrar /group/new")
print("   2. El grupo 'macro_0_demo' debe existir")
print("   3. Las fuentes 0,1,2 deben estar en el grupo")
print("   4. Las posiciones deben actualizarse")
