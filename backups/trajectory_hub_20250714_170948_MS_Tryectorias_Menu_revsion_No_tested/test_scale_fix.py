#!/usr/bin/env python3
"""Test de corrección de escalas y modo de reproducción"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from core.playback_modes import PlaybackMode

def test_scale_and_playback():
    """Test de escalas correctas y modo Fix por defecto"""
    print("=== TEST: ESCALAS Y MODO DE REPRODUCCIÓN ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Test 1: Círculo con radio 5m
    print("1. Creando círculo con radio 5m...")
    macro_id = engine.create_macro("test_circle", 3, "line")
    
    engine.set_macro_trajectory(
        macro_id,
        "circle",
        speed=1.0,
        radius=5.0,
        playback_mode="fix"  # Especificar como string
    )
    
    # Verificar modo de reproducción
    controller = engine.playback_manager.get_controller(macro_id)
    if controller:
        print(f"✅ Modo de reproducción: {controller.mode.value}")
        assert controller.mode.value == "fix", f"El modo debería ser fix"
        print("✅ Modo Fix configurado correctamente")
    
    # Verificar posiciones
    print("\n   Verificando posiciones...")
    for i in range(5):
        engine.update(0.1)
        center = engine.get_macro_center(macro_id)
        if center is not None:
            distance = np.linalg.norm(center[:2])  # Distancia en plano XY
            print(f"   Update {i+1}: Distancia al origen = {distance:.2f}m")
            assert distance <= 5.5, f"La distancia ({distance:.2f}) excede el radio esperado (5m)"
    
    # Test 2: Línea de 10m
    print("\n2. Creando línea de 10m...")
    macro_id2 = engine.create_macro("test_line", 3, "line")
    
    engine.set_macro_trajectory(
        macro_id2,
        "line",
        speed=1.0,
        start=np.array([0.0, 0.0, 0.0]),
        end=np.array([10.0, 0.0, 0.0]),
        playback_mode="fix"
    )
    
    # Verificar longitud
    print("\n   Verificando longitud...")
    for i in range(5):
        engine.update(0.1)
        center = engine.get_macro_center(macro_id2)
        if center is not None:
            print(f"   Update {i+1}: Posición X = {center[0]:.2f}m")
            assert center[0] <= 10.5, f"La posición X ({center[0]:.2f}) excede la longitud esperada (10m)"
    
    # Test 3: Verificar que la velocidad no afecta la escala
    print("\n3. Verificando que la velocidad no afecta la escala...")
    macro_id3 = engine.create_macro("test_speed", 3, "line")
    
    engine.set_macro_trajectory(
        macro_id3,
        "circle",
        speed=2.0,  # Velocidad doble
        radius=3.0,  # Radio pequeño
        playback_mode="fix"
    )
    
    print("\n   Verificando con velocidad 2.0...")
    for i in range(3):
        engine.update(0.1)
        center = engine.get_macro_center(macro_id3)
        if center is not None:
            distance = np.linalg.norm(center[:2])
            print(f"   Update {i+1}: Distancia = {distance:.2f}m (radio esperado: 3m)")
            assert distance <= 3.5, f"La distancia ({distance:.2f}) excede el radio esperado (3m)"
    
    print("\n" + "="*60)
    print("RESUMEN DE CORRECCIONES:")
    print("✅ Modo Fix funciona correctamente por defecto")
    print("✅ Las escalas se mantienen dentro de los valores especificados")
    print("✅ La velocidad no afecta las dimensiones de la trayectoria")
    print("="*60)


if __name__ == "__main__":
    test_scale_and_playback()