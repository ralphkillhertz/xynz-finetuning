#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST CONCENTRACIÓN CON MOVIMIENTO\n")

engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

print("📍 Posiciones iniciales:")
print(f"   Fuente 0: {engine._positions[0]}")
print(f"   Fuente 1: {engine._positions[1]}")
dist_inicial = np.linalg.norm(engine._positions[0] - engine._positions[1])
print(f"   Distancia: {dist_inicial:.2f}")

print("\n🎯 Aplicando concentración...")
engine.set_macro_concentration(macro_id, 0.8)

print("\n🔄 Ejecutando 30 frames...")
for i in range(30):
    engine.step()
    if i % 10 == 9:
        dist = np.linalg.norm(engine._positions[0] - engine._positions[1])
        print(f"   Frame {i+1}: distancia = {dist:.2f}")

print("\n📍 Posiciones finales:")
print(f"   Fuente 0: {engine._positions[0]}")
print(f"   Fuente 1: {engine._positions[1]}")
dist_final = np.linalg.norm(engine._positions[0] - engine._positions[1])
print(f"   Distancia: {dist_final:.2f}")

reduccion = (1 - dist_final/dist_inicial) * 100
print(f"\n📊 Reducción: {reduccion:.1f}%")

if reduccion > 20:
    print("\n✅ ¡CONCENTRACIÓN FUNCIONA PERFECTAMENTE!")
    print("\n🚀 Ahora puedes usar el controlador interactivo:")
    print("   python trajectory_hub/interface/interactive_controller.py")
else:
    print("\n⚠️ Movimiento insuficiente")
    print("   Verifica que step() tenga la lógica de concentración")
