#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST CONCENTRACIÓN (Método probado)\n")

engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

# Posiciones iniciales
print("Antes:")
print(f"  Fuente 0: {engine._positions[0]}")
print(f"  Fuente 1: {engine._positions[1]}")

# Aplicar concentración
engine.set_macro_concentration(macro_id, 0.5)

# Ejecutar 10 frames
for _ in range(10):
    engine.step()

print("\nDespués de 10 frames:")
print(f"  Fuente 0: {engine._positions[0]}")
print(f"  Fuente 1: {engine._positions[1]}")

# Verificar
dispersión_inicial = 4.0
dispersión_final = np.linalg.norm(engine._positions[0] - engine._positions[1])
reducción = (1 - dispersión_final/dispersión_inicial) * 100

print(f"\nReducción: {reducción:.1f}%")
if reducción > 10:
    print("✅ ¡CONCENTRACIÓN FUNCIONA!")
