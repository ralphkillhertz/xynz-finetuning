#!/usr/bin/env python3
"""Test de concentración con sistema de deltas"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trajectory_hub import EnhancedTrajectoryEngine
import numpy as np
import time

def test():
    print("🧪 Test de concentración con deltas\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10, update_rate=60)
    
    # Crear fuentes primero
    source_ids = list(range(5))
    
    # Crear macro
    engine.create_macro("test", list(range(5)))
    
    # Posiciones iniciales dispersas
    for i in range(5):
        angle = i * 2 * np.pi / 5
        engine._positions[i] = np.array([
            np.cos(angle) * 10,
            np.sin(angle) * 10,
            0
        ])
    
    print("Posiciones iniciales:")
    for i in range(5):
        print(f"  Source {i}: {engine._positions[i]}")
    
    # Aplicar concentración
    print("\n✨ Aplicando concentración...")
    engine.apply_concentration("test", factor=0.5)
    
    # Simular algunos frames
    for frame in range(30):
        engine.step()
        if frame % 10 == 0:
            print(f"\nFrame {frame}:")
            center = np.mean(engine._positions[:5], axis=0)
            spread = np.std(engine._positions[:5])
            print(f"  Centro: {center}")
            print(f"  Dispersión: {spread:.2f}")
    
    print("\n✅ Test completado!")

if __name__ == "__main__":
    test()
