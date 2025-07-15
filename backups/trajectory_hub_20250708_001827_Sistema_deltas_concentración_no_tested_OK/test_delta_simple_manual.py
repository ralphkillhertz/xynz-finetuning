#!/usr/bin/env python3
"""Test simplificado que evita problemas con create_source"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.motion_components import SourceMotion, ConcentrationComponent

print("🧪 TEST SIMPLIFICADO DEL SISTEMA DE DELTAS\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=5, fps=60)
print("✅ Engine creado")

# Crear macro SIN usar create_source
source_ids = [0, 1, 2]
from trajectory_hub.core.enhanced_trajectory_engine import Macro

# Crear macro directamente
macro = Macro("test", source_ids)
engine._macros["test"] = macro
print("✅ Macro creado directamente")

# Crear motion states manualmente
for sid in source_ids:
    engine.motion_states[sid] = SourceMotion(sid)
print(f"✅ Motion states creados: {list(engine.motion_states.keys())}")

# Posiciones iniciales
for i in source_ids:
    angle = i * 2 * np.pi / 3
    engine._positions[i] = np.array([np.cos(angle) * 10, np.sin(angle) * 10, 0])

print("\n📍 Posiciones iniciales:")
for i in source_ids:
    pos = engine._positions[i]
    print(f"   Source {i}: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]")

# Distancia inicial
center = np.mean([engine._positions[i] for i in source_ids], axis=0)
dist_inicial = np.mean([np.linalg.norm(engine._positions[i] - center) for i in source_ids])
print(f"\n📏 Distancia inicial al centro: {dist_inicial:.2f}")

# Aplicar concentración
print("\n🎯 Aplicando concentración...")
try:
    # Manualmente añadir ConcentrationComponent
    for sid in source_ids:
        motion = engine.motion_states[sid]
        conc = ConcentrationComponent(macro)
        conc.enabled = True
        conc.concentration_factor = 0.8
        conc.macro_center = center
        motion.add_component(conc)
    
    print("✅ Concentración configurada manualmente")
except Exception as e:
    print(f"❌ Error: {e}")

# Simular
print("\n🔄 Simulando 20 frames...")
for frame in range(20):
    engine.step()
    
    if frame % 5 == 0:
        center = np.mean([engine._positions[i] for i in source_ids], axis=0)
        dist = np.mean([np.linalg.norm(engine._positions[i] - center) for i in source_ids])
        print(f"   Frame {frame}: distancia = {dist:.2f}")

# Resultado final
center_final = np.mean([engine._positions[i] for i in source_ids], axis=0)
dist_final = np.mean([np.linalg.norm(engine._positions[i] - center_final) for i in source_ids])

print(f"\n📊 Resultado:")
print(f"   Distancia inicial: {dist_inicial:.2f}")
print(f"   Distancia final:   {dist_final:.2f}")
print(f"   Cambio:           {dist_final - dist_inicial:.2f}")

if dist_final < dist_inicial:
    print("\n✅ ¡Las fuentes se están concentrando!")
else:
    print("\n❌ Las fuentes NO se están concentrando")
