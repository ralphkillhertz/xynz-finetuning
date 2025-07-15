"""
Ejemplos de componentes de movimiento integrados con el sistema Amount
"""
import numpy as np
from typing import Optional
from .motion_components import MotionComponent, MotionState, MotionDelta
from .amount_system import IntensityAmount, LinearAmount, AngularAmount, ScaleAmount
from .amount_types import WaveAmount, NoiseAmount, VectorAmount


class CircularMotionWithAmounts(MotionComponent):
    """Movimiento circular con control de amounts para todos los parámetros"""
    
    def __init__(self):
        super().__init__("circular_with_amounts")
        
        # Configurar amounts por defecto
        self.add_amount('radius', LinearAmount(5.0, 0.1, 50.0))  # Radio en metros
        self.add_amount('speed', AngularAmount(1.0, -10.0, 10.0))  # Velocidad angular
        self.add_amount('amplitude', IntensityAmount(1.0))  # Amplitud general
        self.add_amount('wobble', WaveAmount(0.0, 2.0, 0.0))  # Oscilación adicional
        self.add_amount('noise', NoiseAmount(0.0))  # Ruido
        
        # Centro del círculo
        self.center = np.zeros(3)
        self.phase = 0.0
        
    def set_parameters(self, radius: float = None, speed: float = None, 
                      amplitude: float = None, wobble_amount: float = None):
        """Configura parámetros usando amounts"""
        if radius is not None:
            self.get_amount('radius').value = radius
        if speed is not None:
            self.get_amount('speed').value = speed
        if amplitude is not None:
            self.get_amount('amplitude').value = amplitude
        if wobble_amount is not None:
            self.get_amount('wobble').value = wobble_amount
            
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Actualiza el estado usando amounts"""
        if not self.enabled:
            return state
            
        # Obtener valores de amounts
        radius = self.get_amount_value('radius', 5.0)
        speed = self.get_amount_value('speed', 1.0)
        amplitude = self.get_amount_value('amplitude', 1.0)
        
        # Actualizar fase
        self.phase += speed * dt
        
        # Calcular posición base en el círculo
        base_x = radius * np.cos(self.phase)
        base_y = radius * np.sin(self.phase)
        base_z = 0.0
        
        # Aplicar wobble si está configurado
        wobble_amount = self.get_amount('wobble')
        if wobble_amount and wobble_amount.value > 0:
            wobble_value = wobble_amount.calculate_value_at_time(current_time)
            base_z += wobble_value
            
        # Posición con amplitud aplicada
        new_position = self.center + np.array([base_x, base_y, base_z]) * amplitude
        
        # Aplicar ruido si está configurado
        noise_amount = self.get_amount('noise')
        if noise_amount and noise_amount.value > 0:
            noise = noise_amount.generate_noise(new_position, current_time)
            new_position += noise * np.array([1, 1, 0.5])  # Menos ruido en Z
            
        # Actualizar estado
        state.position = new_position
        state.velocity = (new_position - state.position) / dt if dt > 0 else np.zeros(3)
        
        return state
        
    def calculate_delta(self, state: MotionState, current_time: float, dt: float) -> MotionDelta:
        """Calcula delta para sistema de deltas"""
        if not self.enabled:
            return MotionDelta()
            
        # Guardar posición actual
        old_position = state.position.copy()
        
        # Actualizar estado
        new_state = self.update(state, current_time, dt)
        
        # Calcular delta
        delta = MotionDelta()
        delta.position = new_state.position - old_position
        
        return delta


class LinearMotionWithAmounts(MotionComponent):
    """Movimiento lineal con sistema de amounts"""
    
    def __init__(self):
        super().__init__("linear_with_amounts")
        
        # Configurar amounts
        self.add_amount('speed', LinearAmount(1.0, 0.0, 10.0))  # m/s
        self.add_amount('acceleration', LinearAmount(0.0, -5.0, 5.0))  # m/s²
        self.add_amount('damping', IntensityAmount(0.0))  # Factor de amortiguación
        
        # Dirección del movimiento
        self.direction = VectorAmount(1.0, 0.0, 0.0)  # Dirección normalizada
        self.current_velocity = 0.0
        
    def set_direction(self, x: float, y: float, z: float):
        """Establece la dirección del movimiento"""
        self.direction.set_from_vector([x, y, z])
        # Normalizar
        norm = self.direction.magnitude
        if norm > 0:
            self.direction.x_amount.value /= norm
            self.direction.y_amount.value /= norm
            self.direction.z_amount.value /= norm
            
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Actualiza posición con movimiento lineal"""
        if not self.enabled:
            return state
            
        # Obtener valores
        target_speed = self.get_amount_value('speed', 1.0)
        acceleration = self.get_amount_value('acceleration', 0.0)
        damping = self.get_amount_value('damping', 0.0)
        
        # Actualizar velocidad con aceleración
        self.current_velocity += acceleration * dt
        
        # Aplicar amortiguación
        if damping > 0:
            self.current_velocity *= (1.0 - damping * dt)
            
        # Limitar a velocidad objetivo
        if acceleration == 0:
            # Interpolar hacia velocidad objetivo
            diff = target_speed - self.current_velocity
            self.current_velocity += diff * min(1.0, 5.0 * dt)
            
        # Calcular desplazamiento
        displacement = self.direction.vector * self.current_velocity * dt
        
        # Actualizar posición
        state.position += displacement
        state.velocity = self.direction.vector * self.current_velocity
        
        return state


class SpiralMotionWithAmounts(MotionComponent):
    """Movimiento en espiral con control completo por amounts"""
    
    def __init__(self):
        super().__init__("spiral_with_amounts")
        
        # Amounts para controlar la espiral
        self.add_amount('initial_radius', LinearAmount(1.0, 0.1, 10.0))
        self.add_amount('expansion_rate', LinearAmount(0.5, -2.0, 2.0))  # m/s
        self.add_amount('rotation_speed', AngularAmount(1.0, -5.0, 5.0))  # rad/s
        self.add_amount('vertical_speed', LinearAmount(0.5, -2.0, 2.0))  # m/s
        self.add_amount('tightness', ScaleAmount(1.0, 0.1, 5.0))  # Factor de apretado
        
        # Estado interno
        self.phase = 0.0
        self.current_radius = 1.0
        self.height = 0.0
        self.center = np.zeros(3)
        
    def update(self, state: MotionState, current_time: float, dt: float) -> MotionState:
        """Actualiza con movimiento en espiral"""
        if not self.enabled:
            return state
            
        # Obtener valores de amounts
        expansion = self.get_amount_value('expansion_rate', 0.5)
        rotation = self.get_amount_value('rotation_speed', 1.0)
        vertical = self.get_amount_value('vertical_speed', 0.5)
        tightness = self.get_amount_value('tightness', 1.0)
        
        # Actualizar parámetros de la espiral
        self.phase += rotation * dt * tightness
        self.current_radius += expansion * dt
        self.height += vertical * dt
        
        # Limitar radio mínimo
        if self.current_radius < 0.1:
            self.current_radius = 0.1
            
        # Calcular posición
        x = self.current_radius * np.cos(self.phase)
        y = self.current_radius * np.sin(self.phase)
        z = self.height
        
        # Actualizar estado
        new_position = self.center + np.array([x, y, z])
        state.velocity = (new_position - state.position) / dt if dt > 0 else np.zeros(3)
        state.position = new_position
        
        return state
        
    def reset(self):
        """Resetea la espiral"""
        super().reset()
        self.phase = 0.0
        self.current_radius = self.get_amount_value('initial_radius', 1.0)
        self.height = 0.0