"""
Mixin para modos de movimiento compartidos entre trayectorias
"""
import numpy as np
from typing import Optional
from enum import Enum

# Definir TrajectoryMovementMode aquí para evitar imports circulares
class TrajectoryMovementMode(Enum):
    """Modos de movimiento para trayectorias"""
    STOP = "stop"
    FIX = "fix"
    RANDOM = "random"
    VIBRATION = "vibration"
    SPIN = "spin"
    FREEZE = "freeze"

class MovementModeMixin:
    """
    Mixin que implementa la lógica de movimiento para trayectorias
    Usado tanto por IndividualTrajectory como MacroTrajectory
    """
    
    def __init__(self):
        # Atributos necesarios para movimiento
        self.position_on_trajectory = 0.0
        self.movement_mode = TrajectoryMovementMode.FIX
        self.movement_speed = 1.0
        self.movement_direction = 1.0  # 1 o -1
        
        # Parámetros para Random
        self.random_timer = 0.0
        self.random_interval = 1.0  # Segundos entre cambios
        self.random_speed_range = (0.5, 2.0)  # Min/max velocidad
        self.random_current_speed = 1.0
        
        # Parámetros para Vibration
        self.vibration_frequency = 5.0  # Hz
        self.vibration_amplitude = 0.1  # Amplitud relativa
        self.vibration_phase = 0.0
        self.vibration_center = 0.0  # Centro de vibración
        
        # Parámetros para Spin
        self.spin_speed = 10.0  # Multiplicador de velocidad
        
        # Parámetros para Freeze
        self.freeze_position = None
        
        # Rampas de aceleración
        self.use_ramps = False
        self.ramp_time = 0.5  # Tiempo de rampa en segundos
        self.current_velocity = 0.0
        self.target_velocity = 0.0
    
    def update_movement(self, dt: float) -> float:
        """
        Actualiza la posición en la trayectoria según el modo
        Retorna la nueva posición
        """
        if self.movement_mode == TrajectoryMovementMode.STOP:
            # Sin movimiento
            return self.position_on_trajectory
            
        elif self.movement_mode == TrajectoryMovementMode.FIX:
            # Velocidad constante con rampas opcionales
            if self.use_ramps:
                self.target_velocity = self.movement_speed * self.movement_direction
                # Suavizar cambios de velocidad
                diff = self.target_velocity - self.current_velocity
                ramp_rate = 1.0 / self.ramp_time if self.ramp_time > 0 else 100.0
                self.current_velocity += np.clip(diff * ramp_rate * dt, -abs(diff), abs(diff))
                self.position_on_trajectory += self.current_velocity * dt
            else:
                # Sin rampas
                self.position_on_trajectory += self.movement_speed * self.movement_direction * dt
                
        elif self.movement_mode == TrajectoryMovementMode.RANDOM:
            # Cambios aleatorios de dirección y velocidad
            self.random_timer += dt
            
            if self.random_timer >= self.random_interval:
                self.random_timer = 0.0
                # Cambiar dirección aleatoriamente
                if np.random.random() < 0.5:
                    self.movement_direction *= -1
                # Nueva velocidad aleatoria
                min_speed, max_speed = self.random_speed_range
                self.random_current_speed = np.random.uniform(min_speed, max_speed)
            
            # Aplicar movimiento con velocidad actual
            self.position_on_trajectory += self.random_current_speed * self.movement_direction * dt
            
        elif self.movement_mode == TrajectoryMovementMode.VIBRATION:
            # Vibración alrededor de un centro
            if self.vibration_center == 0.0:
                self.vibration_center = self.position_on_trajectory
            
            # Actualizar fase de vibración
            self.vibration_phase += 2 * np.pi * self.vibration_frequency * dt
            
            # Calcular posición con vibración
            vibration_offset = self.vibration_amplitude * np.sin(self.vibration_phase)
            self.position_on_trajectory = self.vibration_center + vibration_offset
            
            # Mover lentamente el centro si hay velocidad base
            if self.movement_speed > 0:
                self.vibration_center += self.movement_speed * 0.1 * dt
                
        elif self.movement_mode == TrajectoryMovementMode.SPIN:
            # Giro muy rápido
            spin_velocity = self.movement_speed * self.spin_speed
            self.position_on_trajectory += spin_velocity * dt
            
        elif self.movement_mode == TrajectoryMovementMode.FREEZE:
            # Congelar en posición actual
            if self.freeze_position is None:
                self.freeze_position = self.position_on_trajectory
            self.position_on_trajectory = self.freeze_position
            
        return self.position_on_trajectory
    
    def set_movement_mode(self, mode: 'TrajectoryMovementMode', **params):
        """Cambiar modo de movimiento con parámetros opcionales"""
        self.movement_mode = mode
        
        # Reset según el modo
        if mode == TrajectoryMovementMode.VIBRATION:
            self.vibration_center = self.position_on_trajectory
            self.vibration_phase = 0.0
            self.vibration_frequency = params.get('frequency', 5.0)
            self.vibration_amplitude = params.get('amplitude', 0.1)
            
        elif mode == TrajectoryMovementMode.RANDOM:
            self.random_timer = 0.0
            self.random_interval = params.get('interval', 1.0)
            self.random_speed_range = params.get('speed_range', (0.5, 2.0))
            self.random_current_speed = self.movement_speed
            
        elif mode == TrajectoryMovementMode.SPIN:
            self.spin_speed = params.get('spin_speed', 10.0)
            
        elif mode == TrajectoryMovementMode.FREEZE:
            self.freeze_position = self.position_on_trajectory
            
        elif mode == TrajectoryMovementMode.FIX:
            self.freeze_position = None
            self.vibration_center = 0.0
            if params.get('use_ramps', False):
                self.use_ramps = True
                self.ramp_time = params.get('ramp_time', 0.5)
    
    def reverse_direction(self):
        """Invertir dirección de movimiento"""
        self.movement_direction *= -1
        
    def set_speed(self, speed: float):
        """Establecer velocidad de movimiento"""
        self.movement_speed = abs(speed)
