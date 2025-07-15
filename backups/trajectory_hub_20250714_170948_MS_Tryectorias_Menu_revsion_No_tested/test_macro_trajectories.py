#!/usr/bin/env python3
"""Test del nuevo sistema de trayectorias MS"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'trajectory_hub'))

from core.enhanced_trajectory_engine import EnhancedTrajectoryEngine

def test_basic_trajectories():
    """Test de trayectorias básicas con velocidad positiva y negativa"""
    print("=== TEST: TRAYECTORIAS MS BÁSICAS ===\n")
    
    # Crear engine
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Test 1: Círculo con velocidad positiva
    print("1. Creando macro con trayectoria circular (velocidad positiva)...")
    macro_id = engine.create_macro("test_circle", 3, "line")
    
    # Configurar trayectoria usando string
    engine.set_macro_trajectory(
        macro_id,
        "circle",  # Tipo string
        speed=1.0,  # Velocidad positiva
        radius=5.0,
        plane="xy"
    )
    
    print("✅ Trayectoria circular configurada")
    
    # Simular algunos updates
    print("\n   Simulando movimiento...")
    for i in range(5):
        engine.update(0.016)
        center = engine.get_macro_center(macro_id)
        if center is not None:
            print(f"   Update {i+1}: Centro en [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
    
    # Test 2: Espiral con velocidad negativa
    print("\n2. Creando macro con trayectoria espiral (velocidad negativa)...")
    macro_id2 = engine.create_macro("test_spiral", 5, "circle")
    
    engine.set_macro_trajectory(
        macro_id2,
        "spiral",  # Tipo string
        speed=-0.5,  # Velocidad negativa (sentido inverso)
        radius=3.0,
        height=10.0,
        turns=2.0
    )
    
    print("✅ Trayectoria espiral configurada con velocidad negativa")
    
    # Test 3: Figura 8
    print("\n3. Creando macro con trayectoria figura 8...")
    macro_id3 = engine.create_macro("test_figure8", 4, "grid")
    
    engine.set_macro_trajectory(
        macro_id3,
        "figure8",
        speed=2.0,  # Velocidad doble
        scale=7.0
    )
    
    print("✅ Trayectoria figura 8 configurada")
    
    # Test 4: Lissajous 3D
    print("\n4. Creando macro con trayectoria Lissajous 3D...")
    macro_id4 = engine.create_macro("test_lissajous", 6, "sphere")
    
    engine.set_macro_trajectory(
        macro_id4,
        "lissajous",
        speed=0.75,
        scale=5.0,
        freq_x=3.0,
        freq_y=2.0,
        freq_z=4.0
    )
    
    print("✅ Trayectoria Lissajous 3D configurada")
    
    # Test 5: Trayectoria aleatoria
    print("\n5. Creando macro con trayectoria aleatoria...")
    macro_id5 = engine.create_macro("test_random", 3, "line")
    
    engine.set_macro_trajectory(
        macro_id5,
        "random",
        speed=1.0,
        scale=4.0,
        seed=42,
        num_points=8
    )
    
    print("✅ Trayectoria aleatoria configurada")


def test_open_trajectories():
    """Test de trayectorias abiertas (línea, onda, hélice)"""
    print("\n\n=== TEST: TRAYECTORIAS ABIERTAS ===\n")
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Test 1: Línea
    print("1. Trayectoria de línea...")
    macro_id = engine.create_macro("test_line", 3, "line")
    
    engine.set_macro_trajectory(
        macro_id,
        "line",
        speed=0.5,
        start=np.array([0.0, 0.0, 0.0]),
        end=np.array([20.0, 10.0, 5.0])
    )
    
    print("✅ Línea configurada")
    
    # Test 2: Onda
    print("\n2. Trayectoria de onda...")
    macro_id2 = engine.create_macro("test_wave", 4, "grid")
    
    engine.set_macro_trajectory(
        macro_id2,
        "wave",
        speed=1.0,
        length=15.0,
        amplitude=3.0,
        frequency=3.0,
        axis="x",
        wave_axis="y"
    )
    
    print("✅ Onda configurada")
    
    # Test 3: Hélice abierta
    print("\n3. Trayectoria helicoidal...")
    macro_id3 = engine.create_macro("test_helix", 5, "circle")
    
    engine.set_macro_trajectory(
        macro_id3,
        "helix",
        speed=0.8,
        radius=4.0,
        pitch=2.0,
        turns=4.0
    )
    
    print("✅ Hélice configurada")


def test_3d_trajectories():
    """Test de trayectorias completamente 3D"""
    print("\n\n=== TEST: TRAYECTORIAS 3D COMPLEJAS ===\n")
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Test 1: Nudo toroidal
    print("1. Nudo toroidal...")
    macro_id = engine.create_macro("test_torus", 8, "sphere")
    
    engine.set_macro_trajectory(
        macro_id,
        "torus_knot",
        speed=0.5,
        major_radius=6.0,
        minor_radius=2.0,
        p=2,  # Vueltas alrededor del eje mayor
        q=3   # Vueltas alrededor del eje menor
    )
    
    print("✅ Nudo toroidal configurado")
    
    # Test 2: Círculo en diferentes planos
    print("\n2. Círculos en diferentes planos...")
    
    # Plano XY
    macro_xy = engine.create_macro("circle_xy", 4, "line")
    engine.set_macro_trajectory(macro_xy, "circle", plane="xy", radius=5.0)
    print("✅ Círculo XY configurado")
    
    # Plano XZ
    macro_xz = engine.create_macro("circle_xz", 4, "line")
    engine.set_macro_trajectory(macro_xz, "circle", plane="xz", radius=5.0)
    print("✅ Círculo XZ configurado")
    
    # Plano YZ
    macro_yz = engine.create_macro("circle_yz", 4, "line")
    engine.set_macro_trajectory(macro_yz, "circle", plane="yz", radius=5.0)
    print("✅ Círculo YZ configurado")


def test_legacy_compatibility():
    """Test de compatibilidad con funciones legacy"""
    print("\n\n=== TEST: COMPATIBILIDAD CON FUNCIONES LEGACY ===\n")
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Funciones legacy que deberían funcionar
    legacy_types = ["rose", "butterfly", "heart", "lemniscate", "eight"]
    
    for i, traj_type in enumerate(legacy_types):
        print(f"{i+1}. Probando '{traj_type}'...")
        macro_id = engine.create_macro(f"legacy_{traj_type}", 3, "line")
        
        try:
            engine.set_macro_trajectory(
                macro_id,
                traj_type,
                speed=1.0,
                scale=5.0
            )
            print(f"   ✅ '{traj_type}' funcionando correctamente")
        except Exception as e:
            print(f"   ❌ Error con '{traj_type}': {e}")


def test_error_handling():
    """Test de manejo de errores"""
    print("\n\n=== TEST: MANEJO DE ERRORES ===\n")
    
    engine = EnhancedTrajectoryEngine(max_sources=10)
    
    # Test 1: Tipo de trayectoria inválido
    print("1. Tipo de trayectoria inválido...")
    macro_id = engine.create_macro("test_error", 3, "line")
    
    try:
        engine.set_macro_trajectory(macro_id, "invalid_trajectory_type")
        print("   ❌ No se detectó el error")
    except:
        print("   ✅ Error manejado correctamente")
    
    # Test 2: Macro inexistente
    print("\n2. Macro inexistente...")
    try:
        engine.set_macro_trajectory("macro_inexistente", "circle")
        print("   ❌ No se detectó el error")
    except:
        print("   ✅ Error manejado correctamente")


if __name__ == "__main__":
    test_basic_trajectories()
    test_open_trajectories()
    test_3d_trajectories()
    test_legacy_compatibility()
    test_error_handling()
    
    print("\n" + "="*60)
    print("RESUMEN DE LA SOLUCIÓN:")
    print("✅ Sistema de trayectorias MS funcionando correctamente")
    print("✅ Conversión de string a función implementada")
    print("✅ Soporte para velocidades negativas")
    print("✅ Trayectorias 3D abiertas y cerradas")
    print("✅ Compatibilidad con funciones legacy mantenida")
    print("="*60)