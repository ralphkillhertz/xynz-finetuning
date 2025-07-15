#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST CONCENTRACIÓN CON DELTAS\n")

# Crear engine con sistema de deltas
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
engine.use_delta_system = True

# Crear macro
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

# Posiciones iniciales
print("📍 Posiciones iniciales:")
for i in range(2):
    print(f"   Fuente {i}: {engine._positions[i]}")

# Configurar concentración
print("\n🎯 Configurando concentración...")
engine.set_macro_concentration(macro_id, 0.5)

# Verificar configuración
if 0 in engine._source_motions:
    motion = engine._source_motions[0]
    print(f"\n🔍 SourceMotion[0]:")
    print(f"   use_delta_system: {motion.use_delta_system}")
    print(f"   Componentes: {list(motion.motion_components.keys())}")

# Actualizar varias veces
print("\n🔄 Actualizando 10 frames...")
for i in range(10):
    engine.update(0.016)
    if i == 0 or i == 9:
        print(f"\n📍 Frame {i+1}:")
        for j in range(2):
            print(f"   Fuente {j}: {engine._positions[j]}")

# Verificar movimiento
center = np.mean([engine._positions[0], engine._positions[1]], axis=0)
dist_to_center = np.linalg.norm(engine._positions[0] - center)
print(f"\n📊 Resultado:")
print(f"   Centro: {center}")
print(f"   Distancia al centro: {dist_to_center:.4f}")

if dist_to_center < 1.8:  # Debería ser < 2.0 si hay concentración
    print("\n✅ ¡CONCENTRACIÓN FUNCIONA!")
else:
    print("\n❌ No hay concentración")
