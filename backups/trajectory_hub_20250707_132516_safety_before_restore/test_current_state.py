#!/usr/bin/env python3
'''Test rápido del estado actual'''

import os
os.environ['DISABLE_OSC'] = '1'  # Solo para test

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

# Test concentración
engine = EnhancedTrajectoryEngine(max_sources=4)
macro_id = engine.create_macro("test", source_count=4)

print("\n🧪 TEST DE CONCENTRACIÓN:")
print(f"Posiciones iniciales: {engine._positions[:4]}")

# Aplicar concentración
engine.set_macro_concentration(macro_id, 0.5)

# Ejecutar varios frames
for _ in range(20):
    engine.step()

print(f"Posiciones finales: {engine._positions[:4]}")

# Calcular movimiento
dispersions = []
for i in range(0, 4, 2):
    dist = np.linalg.norm(engine._positions[i] - engine._positions[i+1])
    dispersions.append(dist)

if sum(dispersions) < 10:
    print("\n✅ CONCENTRACIÓN FUNCIONA")
else:
    print("\n❌ Concentración NO funciona")

print("\n📝 PRÓXIMO PASO:")
print("Retomar implementación del sistema paralelo de deltas")
