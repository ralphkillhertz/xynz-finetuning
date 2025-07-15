"""
playback_modes.py - Sistema de modos de reproducción para trayectorias
Implementa Fix, Random, Freeze/Unfreeze, Vibration, Spin
"""
import numpy as np
from enum import Enum
from typing import Optional, Callable, Dict, Any
import time
import random


class PlaybackMode(Enum):
    """Modos de reproducción disponibles"""
    FIX = "fix"  # Velocidad fija
    RANDOM = "random"  # Velocidad y dirección aleatorias
    FREEZE = "freeze"  # Congelado en posición actual
    VIBRATION = "vibration"  # Vibración alrededor de la posición
    SPIN = "spin"  # Rotación continua con variación


class PlaybackController:
    """Controlador de modos de reproducción para trayectorias"""
    
    def __init__(self):
        self.mode = PlaybackMode.FIX
        self.base_speed = 1.0
        self.is_frozen = False
        self.freeze_position = 0.0
        
        # Estado para modo Random
        self.random_speed = 1.0
        self.random_direction = 1.0
        self.random_change_interval = 2.0  # segundos
        self.last_random_change = time.time()
        self.random_speed_range = (0.1, 3.0)
        
        # Estado para modo Vibration
        self.vibration_amplitude = 0.05
        self.vibration_frequency = 10.0
        self.vibration_time = 0.0
        
        # Estado para modo Spin
        self.spin_base_speed = 1.0
        self.spin_variation = 0.5
        self.spin_frequency = 0.2
        self.spin_time = 0.0
        
    def set_mode(self, mode: PlaybackMode, **kwargs):
        """Establece el modo de reproducción con parámetros"""
        self.mode = mode
        
        # Configurar parámetros específicos del modo
        if mode == PlaybackMode.FIX:
            self.base_speed = kwargs.get("speed", 1.0)
            
        elif mode == PlaybackMode.RANDOM:
            self.random_change_interval = kwargs.get("change_interval", 2.0)
            self.random_speed_range = kwargs.get("speed_range", (0.1, 3.0))
            self._update_random_values()
            
        elif mode == PlaybackMode.VIBRATION:
            self.vibration_amplitude = kwargs.get("amplitude", 0.05)
            self.vibration_frequency = kwargs.get("frequency", 10.0)
            self.vibration_time = 0.0
            
        elif mode == PlaybackMode.SPIN:
            self.spin_base_speed = kwargs.get("base_speed", 1.0)
            self.spin_variation = kwargs.get("variation", 0.5)
            self.spin_frequency = kwargs.get("frequency", 0.2)
            self.spin_time = 0.0
    
    def freeze(self, current_position: float):
        """Congela la trayectoria en la posición actual"""
        self.is_frozen = True
        self.freeze_position = current_position
    
    def unfreeze(self):
        """Descongela la trayectoria"""
        self.is_frozen = False
    
    def update(self, delta_time: float, current_t: float) -> float:
        """
        Actualiza y retorna el nuevo valor de t según el modo activo
        
        Args:
            delta_time: Tiempo transcurrido desde última actualización
            current_t: Valor actual del parámetro t (0-1)
            
        Returns:
            Nuevo valor de t modificado según el modo
        """
        # Si está congelado, retornar posición congelada
        if self.is_frozen:
            return self.freeze_position
        
        # Procesar según modo activo
        if self.mode == PlaybackMode.FIX:
            return self._update_fix_mode(delta_time, current_t)
            
        elif self.mode == PlaybackMode.RANDOM:
            return self._update_random_mode(delta_time, current_t)
            
        elif self.mode == PlaybackMode.VIBRATION:
            return self._update_vibration_mode(delta_time, current_t)
            
        elif self.mode == PlaybackMode.SPIN:
            return self._update_spin_mode(delta_time, current_t)
            
        elif self.mode == PlaybackMode.FREEZE:
            # En modo freeze, mantener posición actual
            return current_t
            
        return current_t
    
    def _update_fix_mode(self, delta_time: float, current_t: float) -> float:
        """Modo Fix: velocidad constante"""
        # La velocidad base ya incluye dirección (negativa para reversa)
        new_t = current_t + (self.base_speed * delta_time)
        return new_t % 1.0
    
    def _update_random_mode(self, delta_time: float, current_t: float) -> float:
        """Modo Random: velocidad y dirección cambiantes"""
        current_time = time.time()
        
        # Cambiar valores aleatorios periódicamente
        if current_time - self.last_random_change > self.random_change_interval:
            self._update_random_values()
            self.last_random_change = current_time
        
        # Aplicar velocidad y dirección aleatorias
        speed = self.random_speed * self.random_direction
        new_t = current_t + (speed * delta_time)
        
        # Manejar límites con rebote suave
        if new_t < 0:
            new_t = -new_t
            self.random_direction = 1.0
        elif new_t > 1:
            new_t = 2.0 - new_t
            self.random_direction = -1.0
            
        return new_t % 1.0
    
    def _update_vibration_mode(self, delta_time: float, current_t: float) -> float:
        """Modo Vibration: oscilación rápida alrededor de la posición"""
        self.vibration_time += delta_time
        
        # Calcular offset de vibración
        vibration_offset = self.vibration_amplitude * np.sin(
            self.vibration_time * self.vibration_frequency * 2 * np.pi
        )
        
        # Aplicar vibración al parámetro t
        vibrated_t = current_t + vibration_offset
        
        # Mantener en rango [0, 1]
        return np.clip(vibrated_t, 0.0, 1.0)
    
    def _update_spin_mode(self, delta_time: float, current_t: float) -> float:
        """Modo Spin: rotación con variación sinusoidal"""
        self.spin_time += delta_time
        
        # Calcular velocidad variable
        speed_variation = np.sin(self.spin_time * self.spin_frequency * 2 * np.pi)
        current_speed = self.spin_base_speed * (1.0 + self.spin_variation * speed_variation)
        
        # Aplicar velocidad variable
        new_t = current_t + (current_speed * delta_time)
        return new_t % 1.0
    
    def _update_random_values(self):
        """Actualiza valores aleatorios para modo Random"""
        self.random_speed = random.uniform(*self.random_speed_range)
        self.random_direction = random.choice([-1.0, 1.0])
    
    def get_effective_speed(self) -> float:
        """Retorna la velocidad efectiva actual según el modo"""
        if self.is_frozen or self.mode == PlaybackMode.FREEZE:
            return 0.0
            
        if self.mode == PlaybackMode.FIX:
            return self.base_speed
            
        elif self.mode == PlaybackMode.RANDOM:
            return self.random_speed * self.random_direction
            
        elif self.mode == PlaybackMode.VIBRATION:
            return 0.0  # La vibración no avanza, solo oscila
            
        elif self.mode == PlaybackMode.SPIN:
            speed_variation = np.sin(self.spin_time * self.spin_frequency * 2 * np.pi)
            return self.spin_base_speed * (1.0 + self.spin_variation * speed_variation)
            
        return self.base_speed


class TrajectoryPlaybackManager:
    """Manager para controlar playback de múltiples trayectorias"""
    
    def __init__(self):
        self.controllers: Dict[str, PlaybackController] = {}
        
    def create_controller(self, trajectory_id: str) -> PlaybackController:
        """Crea un nuevo controlador de playback"""
        controller = PlaybackController()
        self.controllers[trajectory_id] = controller
        return controller
    
    def get_controller(self, trajectory_id: str) -> Optional[PlaybackController]:
        """Obtiene el controlador para una trayectoria"""
        return self.controllers.get(trajectory_id)
    
    def remove_controller(self, trajectory_id: str):
        """Elimina un controlador"""
        if trajectory_id in self.controllers:
            del self.controllers[trajectory_id]
    
    def set_mode_for_trajectory(self, trajectory_id: str, mode: PlaybackMode, **kwargs):
        """Establece el modo de reproducción para una trayectoria específica"""
        controller = self.get_controller(trajectory_id)
        if controller:
            controller.set_mode(mode, **kwargs)
    
    def freeze_trajectory(self, trajectory_id: str, current_position: float):
        """Congela una trayectoria específica"""
        controller = self.get_controller(trajectory_id)
        if controller:
            controller.freeze(current_position)
    
    def unfreeze_trajectory(self, trajectory_id: str):
        """Descongela una trayectoria específica"""
        controller = self.get_controller(trajectory_id)
        if controller:
            controller.unfreeze()
    
    def freeze_all(self, current_positions: Dict[str, float]):
        """Congela todas las trayectorias"""
        for traj_id, position in current_positions.items():
            self.freeze_trajectory(traj_id, position)
    
    def unfreeze_all(self):
        """Descongela todas las trayectorias"""
        for controller in self.controllers.values():
            controller.unfreeze()