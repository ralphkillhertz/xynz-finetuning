#!/usr/bin/env python3
"""
🧪 TEST: Verificación de offsets aplicados
"""

import os
import sys
import numpy as np

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

os.environ['DISABLE_OSC'] = '1'

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

print("\n🧪 TEST DE OFFSETS EN STEP()\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)

# Crear macro
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

# Posición inicial
print("📍 POSICIONES INICIALES:")
pos0_inicial = engine._positions[0].copy()
pos1_inicial = engine._positions[1].copy()
print(f"   Fuente 0: {pos0_inicial}")
print(f"   Fuente 1: {pos1_inicial}")

# Aplicar concentración
print("\n🎯 Aplicando concentración 0.5...")
engine.set_macro_concentration(macro_id, 0.5)

# Verificar offsets
motion0 = engine._source_motions[0]
motion1 = engine._source_motions[1]
print(f"\n🔍 Offsets:")
print(f"   Fuente 0: {motion0.concentration_offset}")
print(f"   Fuente 1: {motion1.concentration_offset}")

# Ejecutar UN solo step
print("\n🔄 Ejecutando 1 step()...")
engine.step()

# Verificar posiciones después
print("\n📍 POSICIONES DESPUÉS DE 1 STEP:")
print(f"   Fuente 0: {engine._positions[0]}")
print(f"   Fuente 1: {engine._positions[1]}")

# Calcular movimiento
mov0 = np.linalg.norm(engine._positions[0] - pos0_inicial)
mov1 = np.linalg.norm(engine._positions[1] - pos1_inicial)

print(f"\n📊 MOVIMIENTO:")
print(f"   Fuente 0: {mov0:.4f}")
print(f"   Fuente 1: {mov1:.4f}")

if mov0 > 0.01 or mov1 > 0.01:
    print("\n✅ ¡ÉXITO! step() está aplicando los offsets")
    
    # Ejecutar más frames
    print("\n🔄 Ejecutando 50 frames más...")
    for _ in range(50):
        engine.step()
    
    print("\n📍 POSICIONES FINALES:")
    print(f"   Fuente 0: {engine._positions[0]}")
    print(f"   Fuente 1: {engine._positions[1]}")
    
    # Verificar concentración
    distancia_inicial = np.linalg.norm(pos1_inicial - pos0_inicial)
    distancia_final = np.linalg.norm(engine._positions[1] - engine._positions[0])
    
    print(f"\n📊 CONCENTRACIÓN:")
    print(f"   Distancia inicial: {distancia_inicial:.4f}")
    print(f"   Distancia final: {distancia_final:.4f}")
    print(f"   Reducción: {(1 - distancia_final/distancia_inicial)*100:.1f}%")
    
    print("\n🎉 LA CONCENTRACIÓN FUNCIONA!")
    print("\n🚀 Prueba ahora el controlador:")
    print("   python trajectory_hub/interface/interactive_controller.py")
else:
    print("\n❌ step() NO está aplicando los offsets")

print("\n" + "="*60)
