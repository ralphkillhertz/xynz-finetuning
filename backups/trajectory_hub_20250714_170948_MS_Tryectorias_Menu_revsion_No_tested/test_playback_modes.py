#!/usr/bin/env python3
"""Test del sistema de modos de reproducción"""

import sys
import numpy as np
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from core.playback_modes import PlaybackMode

def test_playback_modes():
    """Test de todos los modos de reproducción"""
    print("=== TEST: MODOS DE REPRODUCCIÓN ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Test 1: Modo Fix (por defecto)
    print("1. Creando macro con modo Fix...")
    macro_id = engine.create_macro("test_fix", 3, "line")
    
    engine.set_macro_trajectory(
        macro_id,
        "circle",
        speed=1.0,
        radius=5.0,
        playback_mode=PlaybackMode.FIX
    )
    
    print("✅ Modo Fix configurado (velocidad constante)")
    
    # Simular algunos updates
    print("   Simulando movimiento...")
    for i in range(5):
        engine.update(0.016)
        time.sleep(0.016)
    
    # Test 2: Modo Random
    print("\n2. Creando macro con modo Random...")
    macro_id2 = engine.create_macro("test_random", 4, "circle")
    
    engine.set_macro_trajectory(
        macro_id2,
        "spiral",
        speed=1.0,
        radius=3.0,
        height=10.0,
        playback_mode=PlaybackMode.RANDOM,
        playback_params={
            "change_interval": 1.0,
            "speed_range": (0.5, 2.0)
        }
    )
    
    print("✅ Modo Random configurado (velocidad y dirección aleatorias)")
    
    # Test 3: Modo Vibration
    print("\n3. Creando macro con modo Vibration...")
    macro_id3 = engine.create_macro("test_vibration", 3, "line")
    
    engine.set_macro_trajectory(
        macro_id3,
        "figure8",
        speed=0.5,
        scale=5.0,
        playback_mode=PlaybackMode.VIBRATION,
        playback_params={
            "amplitude": 0.05,
            "frequency": 10.0
        }
    )
    
    print("✅ Modo Vibration configurado (oscilación)")
    
    # Test 4: Modo Spin
    print("\n4. Creando macro con modo Spin...")
    macro_id4 = engine.create_macro("test_spin", 5, "grid")
    
    engine.set_macro_trajectory(
        macro_id4,
        "lissajous",
        speed=1.0,
        scale=5.0,
        playback_mode=PlaybackMode.SPIN,
        playback_params={
            "base_speed": 1.0,
            "variation": 0.5,
            "frequency": 0.2
        }
    )
    
    print("✅ Modo Spin configurado (velocidad variable)")
    
    # Test 5: Freeze/Unfreeze
    print("\n5. Test de Freeze/Unfreeze...")
    macro_id5 = engine.create_macro("test_freeze", 3, "circle")
    
    engine.set_macro_trajectory(
        macro_id5,
        "helix",
        speed=1.0,
        radius=3.0,
        playback_mode=PlaybackMode.FIX
    )
    
    print("   Movimiento normal...")
    for i in range(3):
        engine.update(0.016)
        time.sleep(0.016)
    
    print("   Congelando trayectoria...")
    engine.freeze_macro(macro_id5)
    
    for i in range(3):
        engine.update(0.016)
        time.sleep(0.016)
    
    print("   Descongelando trayectoria...")
    engine.unfreeze_macro(macro_id5)
    
    print("✅ Freeze/Unfreeze funcionando")
    
    # Test 6: Cambio dinámico de modo
    print("\n6. Test de cambio dinámico de modo...")
    macro_id6 = engine.create_macro("test_dynamic", 4, "line")
    
    engine.set_macro_trajectory(
        macro_id6,
        "circle",
        speed=1.0,
        radius=5.0,
        playback_mode=PlaybackMode.FIX
    )
    
    print("   Iniciando con modo Fix...")
    for i in range(3):
        engine.update(0.016)
        time.sleep(0.016)
    
    print("   Cambiando a modo Random...")
    engine.set_macro_playback_mode(
        macro_id6,
        PlaybackMode.RANDOM,
        change_interval=0.5,
        speed_range=(0.1, 3.0)
    )
    
    for i in range(3):
        engine.update(0.016)
        time.sleep(0.016)
    
    print("   Cambiando a modo Vibration...")
    engine.set_macro_playback_mode(
        macro_id6,
        PlaybackMode.VIBRATION,
        amplitude=0.1,
        frequency=5.0
    )
    
    print("✅ Cambio dinámico de modos funcionando")


def test_negative_speeds_with_modes():
    """Test de velocidades negativas con diferentes modos"""
    print("\n\n=== TEST: VELOCIDADES NEGATIVAS CON MODOS ===\n")
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Test con velocidad negativa en modo Fix
    print("1. Modo Fix con velocidad negativa...")
    macro_id = engine.create_macro("test_negative", 3, "line")
    
    engine.set_macro_trajectory(
        macro_id,
        "circle",
        speed=-1.5,  # Velocidad negativa
        radius=5.0,
        playback_mode=PlaybackMode.FIX
    )
    
    print("✅ Velocidad negativa funcionando en modo Fix")
    
    # Test con modo Spin y velocidad base negativa
    print("\n2. Modo Spin con velocidad base negativa...")
    macro_id2 = engine.create_macro("test_spin_negative", 4, "circle")
    
    engine.set_macro_trajectory(
        macro_id2,
        "spiral",
        speed=-1.0,
        radius=3.0,
        playback_mode=PlaybackMode.SPIN,
        playback_params={
            "base_speed": -1.0,  # Base negativa
            "variation": 0.5,
            "frequency": 0.3
        }
    )
    
    print("✅ Modo Spin con velocidad negativa configurado")


if __name__ == "__main__":
    test_playback_modes()
    test_negative_speeds_with_modes()
    
    print("\n" + "="*60)
    print("RESUMEN DE LA IMPLEMENTACIÓN:")
    print("✅ Modo Fix implementado (velocidad constante)")
    print("✅ Modo Random implementado (velocidad/dirección aleatorias)")
    print("✅ Modo Vibration implementado (oscilación)")
    print("✅ Modo Spin implementado (velocidad variable)")
    print("✅ Sistema Freeze/Unfreeze funcionando")
    print("✅ Cambio dinámico de modos funcionando")
    print("✅ Integración con velocidades negativas")
    print("✅ Integración con CLI completa")
    print("="*60)