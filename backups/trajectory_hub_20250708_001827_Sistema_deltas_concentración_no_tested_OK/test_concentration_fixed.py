#!/usr/bin/env python3
"""Test de concentración con sistema de deltas - Versión corregida"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

def test():
    print("🧪 Test de concentración con deltas\n")
    
    # Crear engine con parámetros correctos
    engine = EnhancedTrajectoryEngine(max_sources=10, update_rate=60)
    
    # IDs de las fuentes
    source_ids = list(range(5))
    
    # Crear macro
    engine.create_macro("test", source_ids)
    
    # Posiciones iniciales dispersas
    for i in source_ids:
        angle = i * 2 * np.pi / 5
        pos = np.array([
            np.cos(angle) * 10,
            np.sin(angle) * 10,
            0
        ])
        # Establecer posición directamente
        if i < len(engine._positions):
            engine._positions[i] = pos
    
    print("Posiciones iniciales:")
    for i in source_ids:
        if i < len(engine._positions):
            print(f"  Source {i}: {engine._positions[i]}")
    
    # Aplicar concentración
    print("\n✨ Aplicando concentración...")
    try:
        engine.apply_concentration("test", factor=0.5)
        print("   Concentración aplicada")
    except AttributeError:
        print("   ⚠️ apply_concentration no existe, intentando set_macro_concentration...")
        try:
            engine.set_macro_concentration("test", factor=0.5)
            print("   Concentración aplicada con set_macro_concentration")
        except:
            print("   ❌ No se pudo aplicar concentración")
            return
    
    # Simular algunos frames
    print("\n📊 Simulando frames...")
    for frame in range(30):
        positions = engine.step()
        
        if frame % 10 == 0:
            print(f"\nFrame {frame}:")
            # Calcular centro y dispersión solo de las fuentes del macro
            macro_positions = positions[:5]
            center = np.mean(macro_positions, axis=0)
            
            # Calcular distancia promedio al centro
            distances = [np.linalg.norm(pos - center) for pos in macro_positions]
            avg_distance = np.mean(distances)
            
            print(f"  Centro: [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
            print(f"  Distancia promedio al centro: {avg_distance:.2f}")
    
    print("\n✅ Test completado!")

if __name__ == "__main__":
    test()
