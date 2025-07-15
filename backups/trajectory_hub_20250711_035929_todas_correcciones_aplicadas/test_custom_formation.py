#!/usr/bin/env python3
"""
Prueba de formaciones personalizadas con funciones matemáticas
"""
import numpy as np
from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_custom_formations():
    """Probar varias formaciones personalizadas"""
    
    engine = EnhancedTrajectoryEngine(max_sources=100)
    
    # Ejemplo 1: Rosa polar
    print("=== 1. ROSA POLAR ===")
    custom_func_rose = {
        'r': '2 + sin(4 * t * 2 * pi)',
        'polar': True,
        'z': 't * 2 - 1'  # Variar Z de -1 a 1
    }
    
    macro1 = engine.create_macro(
        name="rosa_polar",
        source_count=30,
        formation="custom",
        spacing=1.5,
        custom_function=custom_func_rose
    )
    
    print(f"✅ Macro 'rosa_polar' creado")
    
    # Ejemplo 2: Espiral 3D
    print("\n=== 2. ESPIRAL 3D ===")
    custom_func_spiral = {
        'x': '(2 + t) * cos(t * 6 * pi)',
        'y': '(2 + t) * sin(t * 6 * pi)',
        'z': 't * 4'
    }
    
    macro2 = engine.create_macro(
        name="espiral_3d",
        source_count=40,
        formation="custom",
        spacing=1.0,
        custom_function=custom_func_spiral
    )
    
    print(f"✅ Macro 'espiral_3d' creado")
    
    # Ejemplo 3: Lemniscata de Bernoulli
    print("\n=== 3. LEMNISCATA ===")
    custom_func_lemniscate = {
        'x': '2 * sqrt(2) * cos(t * 2 * pi) / (1 + sin(t * 2 * pi) ** 2)',
        'y': '2 * sqrt(2) * cos(t * 2 * pi) * sin(t * 2 * pi) / (1 + sin(t * 2 * pi) ** 2)',
        'z': 'sin(t * 4 * pi)'
    }
    
    macro3 = engine.create_macro(
        name="lemniscata",
        source_count=50,
        formation="custom",
        spacing=1.2,
        custom_function=custom_func_lemniscate
    )
    
    print(f"✅ Macro 'lemniscata' creado")
    
    # Ejemplo 4: Toroide
    print("\n=== 4. TOROIDE ===")
    custom_func_torus = {
        'x': '(3 + cos(i * 2 * pi / sqrt(n))) * cos(t * 2 * pi)',
        'y': '(3 + cos(i * 2 * pi / sqrt(n))) * sin(t * 2 * pi)',
        'z': 'sin(i * 2 * pi / sqrt(n))'
    }
    
    macro4 = engine.create_macro(
        name="toroide",
        source_count=64,  # 8x8 grid
        formation="custom",
        spacing=0.8,
        custom_function=custom_func_torus
    )
    
    print(f"✅ Macro 'toroide' creado")
    
    # Verificar posiciones del último macro
    print("\n📍 Primeras 5 posiciones del toroide:")
    for i in range(5):
        if i < len(engine._positions):
            pos = engine._positions[64 - 5 + i]  # Últimas fuentes creadas
            print(f"  Fuente {i}: x={pos[0]:.3f}, y={pos[1]:.3f}, z={pos[2]:.3f}")
    
    print("\n✨ Todas las formaciones personalizadas creadas exitosamente")
    print("   Verifica en SPAT para ver las formas 3D")

if __name__ == "__main__":
    test_custom_formations()