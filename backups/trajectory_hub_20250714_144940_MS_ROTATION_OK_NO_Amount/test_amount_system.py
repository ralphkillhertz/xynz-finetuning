#!/usr/bin/env python3
"""
Test del sistema Amount/Magnitude integrado
"""
import sys
import time
import numpy as np
from trajectory_hub.core.amount_system import (
    IntensityAmount, LinearAmount, AngularAmount, ScaleAmount,
    create_rotation_amount, create_speed_amount, create_distance_amount
)
from trajectory_hub.core.amount_types import (
    ForceAmount, WaveAmount, NoiseAmount, VectorAmount
)
from trajectory_hub.core.motion_with_amounts import (
    CircularMotionWithAmounts, LinearMotionWithAmounts, SpiralMotionWithAmounts
)
from trajectory_hub.core.motion_components import MotionState


def test_basic_amounts():
    """Test de amounts básicos"""
    print("\n=== TEST AMOUNTS BÁSICOS ===")
    
    # Intensity Amount
    intensity = IntensityAmount(0.5)
    print(f"Intensity: {intensity.value} (normalizado: {intensity.normalized})")
    
    # Linear Amount  
    distance = LinearAmount(10.0, 0.0, 100.0)
    print(f"Distance: {distance.value}m (normalizado: {distance.normalized})")
    
    # Angular Amount
    angle = AngularAmount(45.0, -180.0, 180.0)
    print(f"Angle: {angle.value}° = {angle.radians:.2f} rad")
    
    # Scale Amount
    scale = ScaleAmount(2.0, 0.1, 10.0)
    print(f"Scale: {scale.value}x")
    
    # Interpolación
    intensity2 = IntensityAmount(1.0)
    interpolated = intensity.interpolate(intensity2, 0.5)
    print(f"\nInterpolación 50%: {interpolated.value}")


def test_advanced_amounts():
    """Test de amounts avanzados"""
    print("\n=== TEST AMOUNTS AVANZADOS ===")
    
    # Force Amount
    force = ForceAmount(5.0, -10.0, 10.0)
    force.falloff_type = "inverse_square"
    force.falloff_range = 10.0
    
    print("Force at distance:")
    for dist in [0, 1, 5, 10, 20]:
        f = force.calculate_force_at_distance(dist)
        print(f"  {dist}m: {f:.2f}")
    
    # Wave Amount
    wave = WaveAmount(amplitude=1.0, frequency=2.0, phase=0.0)
    wave.waveform = "sine"
    
    print("\nWave values over time:")
    for t in [0, 0.25, 0.5, 0.75, 1.0]:
        v = wave.calculate_value_at_time(t)
        print(f"  t={t}: {v:.2f}")
    
    # Noise Amount
    noise = NoiseAmount(0.1)
    noise.noise_type = "perlin"
    pos = np.array([1.0, 2.0, 3.0])
    
    print(f"\nNoise at position {pos}:")
    for t in range(5):
        n = noise.generate_noise(pos, t * 0.1)
        print(f"  t={t*0.1}: {n:.3f}")
    
    # Vector Amount
    vec = VectorAmount(1.0, 0.0, 0.5)
    print(f"\nVector: {vec.vector}")
    print(f"Magnitude: {vec.magnitude:.2f}")
    print(f"Normalized: {vec.normalized_vector}")


def test_motion_with_amounts():
    """Test de componentes de movimiento con amounts"""
    print("\n=== TEST MOVIMIENTO CON AMOUNTS ===")
    
    # Circular motion
    circular = CircularMotionWithAmounts()
    circular.set_parameters(radius=5.0, speed=1.0, amplitude=0.8, wobble_amount=0.2)
    
    state = MotionState()
    print("\nMovimiento circular con amounts:")
    for i in range(5):
        state = circular.update(state, i * 0.1, 0.1)
        print(f"  t={i*0.1}: pos={state.position}")
    
    # Linear motion
    linear = LinearMotionWithAmounts()
    linear.set_direction(1.0, 0.5, 0.0)
    linear.get_amount('speed').value = 2.0
    linear.get_amount('acceleration').value = 0.5
    
    state2 = MotionState()
    print("\nMovimiento lineal con amounts:")
    for i in range(5):
        state2 = linear.update(state2, i * 0.1, 0.1)
        print(f"  t={i*0.1}: pos={state2.position}, vel={linear.current_velocity:.2f}")
    
    # Spiral motion
    spiral = SpiralMotionWithAmounts()
    spiral.get_amount('initial_radius').value = 1.0
    spiral.get_amount('expansion_rate').value = 0.5
    spiral.get_amount('rotation_speed').value = 2.0
    spiral.get_amount('vertical_speed').value = 0.3
    
    state3 = MotionState()
    print("\nMovimiento espiral con amounts:")
    for i in range(5):
        state3 = spiral.update(state3, i * 0.1, 0.1)
        print(f"  t={i*0.1}: pos={state3.position}, r={spiral.current_radius:.2f}")


def test_factory_functions():
    """Test de funciones factory"""
    print("\n=== TEST FACTORY FUNCTIONS ===")
    
    rotation_amount = create_rotation_amount(0.75)
    print(f"Rotation amount: {rotation_amount.value} ({rotation_amount.name})")
    
    speed_amount = create_speed_amount(1.5)
    print(f"Speed amount: {speed_amount.value}x ({speed_amount.name})")
    
    distance_amount = create_distance_amount(25.0)
    print(f"Distance amount: {distance_amount.value}m ({distance_amount.name})")


def main():
    """Ejecuta todos los tests"""
    print("=== SISTEMA AMOUNT/MAGNITUDE - TESTS ===")
    
    test_basic_amounts()
    test_advanced_amounts()
    test_motion_with_amounts()
    test_factory_functions()
    
    print("\n✅ Todos los tests completados")


if __name__ == "__main__":
    main()