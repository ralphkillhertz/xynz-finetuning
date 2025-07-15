#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("🧪 TEST COMPLETO DEL SISTEMA OSC\n")

# Crear engine
print("1. Iniciando engine...")
engine = EnhancedTrajectoryEngine(max_sources=10, fps=60)

# Crear varios macros
print("\n2. Creando macros...")
macro1 = engine.create_macro("Pajaros", source_count=3, formation="triangle")
macro2 = engine.create_macro("Insectos", source_count=4, formation="grid")

# Aplicar comportamientos
print("\n3. Aplicando concentración...")
engine.set_macro_concentration(macro1, 0.7)
engine.set_macro_concentration(macro2, 0.3)

# Ejecutar algunos frames
print("\n4. Ejecutando simulación...")
for i in range(10):
    engine.step()
    if i % 5 == 0:
        print(f"   Frame {i}")

print("\n✅ VERIFICA EN SPAT:")
print("   1. Grupos 'Pajaros' e 'Insectos' creados")
print("   2. Fuentes 0-2 en 'Pajaros'")
print("   3. Fuentes 3-6 en 'Insectos'")
print("   4. Todas las fuentes moviéndose")
print("   5. Concentración visible")

print("\n🚀 Si todo funciona, ejecuta:")
print("   python trajectory_hub/interface/interactive_controller.py")
