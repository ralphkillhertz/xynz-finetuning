#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
import numpy as np

print("🧪 TEST FINAL CONCENTRACIÓN\n")

engine = EnhancedTrajectoryEngine(max_sources=4, fps=60)
macro_id = engine.create_macro("test", source_count=2, formation="line", spacing=4.0)

print("1. Configurando concentración...")
engine.set_macro_concentration(macro_id, 0.8)

# Verificar que se guardó
macro = engine._macros[macro_id]
factor = getattr(macro, 'concentration_factor', None)
print(f"   Factor guardado: {factor}")

if factor is None:
    print("\n❌ FALLO: concentration_factor no se guardó")
    print("   Revisa que set_macro_concentration esté bien implementado")
else:
    print("\n2. Posiciones iniciales:")
    for i in range(2):
        print(f"   Fuente {i}: {engine._positions[i]}")
    
    print("\n3. Ejecutando 20 frames...")
    for _ in range(20):
        engine.step()
    
    print("\n4. Posiciones finales:")
    for i in range(2):
        print(f"   Fuente {i}: {engine._positions[i]}")
    
    # Verificar convergencia
    dist_inicial = 4.0
    dist_final = np.linalg.norm(engine._positions[0] - engine._positions[1])
    
    print(f"\nDistancia inicial: {dist_inicial:.2f}")
    print(f"Distancia final: {dist_final:.2f}")
    print(f"Reducción: {(1 - dist_final/dist_inicial)*100:.1f}%")
    
    if dist_final < dist_inicial * 0.9:
        print("\n✅ ¡CONCENTRACIÓN FUNCIONA!")
    else:
        print("\n❌ No hay concentración suficiente")
