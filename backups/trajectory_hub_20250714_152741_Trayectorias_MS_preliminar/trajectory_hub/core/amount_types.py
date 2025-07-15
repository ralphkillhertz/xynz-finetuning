"""
Tipos específicos de Amount para diferentes componentes del sistema
"""
import numpy as np
from typing import Optional, Tuple, List, Any
from .amount_system import (
    Amount, AmountType, AmountUnit, 
    IntensityAmount, LinearAmount, AngularAmount
)


class ForceAmount(Amount):
    """Amount para fuerzas de atracción/repulsión"""
    
    def __init__(self, 
                 value: float = 1.0,
                 min_value: float = -10.0,
                 max_value: float = 10.0):
        super().__init__(value, min_value, max_value, 
                        AmountUnit.MULTIPLIER, AmountType.FORCE)
        self.falloff_type = "inverse_square"  # linear, inverse, inverse_square
        self.falloff_range = 10.0  # Rango de influencia
        
    def calculate_force_at_distance(self, distance: float) -> float:
        """Calcula la fuerza considerando la distancia"""
        if distance <= 0:
            return self._value
            
        if self.falloff_type == "linear":
            factor = max(0, 1 - distance / self.falloff_range)
        elif self.falloff_type == "inverse":
            factor = 1 / (1 + distance / self.falloff_range)
        elif self.falloff_type == "inverse_square":
            factor = 1 / (1 + (distance / self.falloff_range) ** 2)
        else:
            factor = 1.0
            
        return self._value * factor
        
    def apply_to(self, vector: np.ndarray, distance: float = 1.0) -> np.ndarray:
        """Aplica la fuerza a un vector considerando distancia"""
        force = self.calculate_force_at_distance(distance)
        return vector * force
        
    def interpolate(self, other: 'ForceAmount', factor: float) -> 'ForceAmount':
        """Interpola entre dos fuerzas"""
        factor = max(0.0, min(1.0, factor))
        new_value = self._value * (1 - factor) + other._value * factor
        result = ForceAmount(new_value, self._min_value, self._max_value)
        result.falloff_type = self.falloff_type
        result.falloff_range = self.falloff_range * (1 - factor) + other.falloff_range * factor
        return result


class WaveAmount(Amount):
    """Amount para ondas y oscilaciones"""
    
    def __init__(self, 
                 amplitude: float = 1.0,
                 frequency: float = 1.0,
                 phase: float = 0.0):
        super().__init__(amplitude, 0.0, 10.0, 
                        AmountUnit.MULTIPLIER, AmountType.WAVE)
        self.frequency = frequency  # Hz
        self.phase = phase  # Radianes
        self.waveform = "sine"  # sine, square, triangle, sawtooth
        
    def calculate_value_at_time(self, time: float) -> float:
        """Calcula el valor de la onda en un momento dado"""
        t = time * self.frequency * 2 * np.pi + self.phase
        
        if self.waveform == "sine":
            wave = np.sin(t)
        elif self.waveform == "square":
            wave = 1.0 if np.sin(t) > 0 else -1.0
        elif self.waveform == "triangle":
            wave = 2 * np.arcsin(np.sin(t)) / np.pi
        elif self.waveform == "sawtooth":
            wave = 2 * ((t / (2 * np.pi)) % 1) - 1
        else:
            wave = 0.0
            
        return wave * self._value
        
    def apply_to(self, value: float, time: float) -> float:
        """Aplica la onda a un valor en un momento dado"""
        return value + self.calculate_value_at_time(time)
        
    def interpolate(self, other: 'WaveAmount', factor: float) -> 'WaveAmount':
        """Interpola entre dos ondas"""
        factor = max(0.0, min(1.0, factor))
        new_amplitude = self._value * (1 - factor) + other._value * factor
        new_frequency = self.frequency * (1 - factor) + other.frequency * factor
        new_phase = self.phase * (1 - factor) + other.phase * factor
        result = WaveAmount(new_amplitude, new_frequency, new_phase)
        result.waveform = self.waveform if factor < 0.5 else other.waveform
        return result


class NoiseAmount(Amount):
    """Amount para ruido y variaciones aleatorias"""
    
    def __init__(self, 
                 intensity: float = 0.1,
                 min_value: float = 0.0,
                 max_value: float = 1.0):
        super().__init__(intensity, min_value, max_value, 
                        AmountUnit.NORMALIZED, AmountType.NOISE)
        self.noise_type = "perlin"  # uniform, gaussian, perlin
        self.octaves = 4
        self.persistence = 0.5
        self.lacunarity = 2.0
        self.seed = None
        self._noise_offset = np.random.rand(3) * 1000
        
    def generate_noise(self, position: np.ndarray, time: float) -> float:
        """Genera ruido basado en posición y tiempo"""
        if self.noise_type == "uniform":
            return np.random.uniform(-1, 1) * self._value
        elif self.noise_type == "gaussian":
            return np.random.normal(0, 1) * self._value
        elif self.noise_type == "perlin":
            # Simplified Perlin-like noise
            x, y, z = position + self._noise_offset
            t = time * 0.1
            
            # Simple implementation using sin waves
            noise = 0
            amplitude = 1
            max_amplitude = 0
            
            for i in range(self.octaves):
                noise += amplitude * np.sin(x * self.lacunarity**i + t)
                noise += amplitude * np.sin(y * self.lacunarity**i + t * 1.1)
                noise += amplitude * np.sin(z * self.lacunarity**i + t * 0.9)
                max_amplitude += amplitude
                amplitude *= self.persistence
                
            return (noise / max_amplitude) * self._value
        
        return 0.0
        
    def apply_to(self, value: np.ndarray, position: np.ndarray, time: float) -> np.ndarray:
        """Aplica ruido a un valor"""
        noise = self.generate_noise(position, time)
        if isinstance(value, np.ndarray):
            noise_vector = np.array([
                self.generate_noise(position + [0.1, 0, 0], time),
                self.generate_noise(position + [0, 0.1, 0], time),
                self.generate_noise(position + [0, 0, 0.1], time)
            ])
            return value + noise_vector
        else:
            return value + noise
            
    def interpolate(self, other: 'NoiseAmount', factor: float) -> 'NoiseAmount':
        """Interpola entre dos ruidos"""
        factor = max(0.0, min(1.0, factor))
        new_intensity = self._value * (1 - factor) + other._value * factor
        result = NoiseAmount(new_intensity, self._min_value, self._max_value)
        result.noise_type = self.noise_type if factor < 0.5 else other.noise_type
        result.octaves = int(self.octaves * (1 - factor) + other.octaves * factor)
        result.persistence = self.persistence * (1 - factor) + other.persistence * factor
        result.lacunarity = self.lacunarity * (1 - factor) + other.lacunarity * factor
        return result


class BlendAmount(Amount):
    """Amount para mezclar entre estados o valores"""
    
    def __init__(self, value: float = 0.5):
        super().__init__(value, 0.0, 1.0, 
                        AmountUnit.NORMALIZED, AmountType.BLEND)
        self.blend_mode = "linear"  # linear, smooth, ease_in, ease_out, ease_in_out
        
    def calculate_blend_factor(self) -> float:
        """Calcula el factor de mezcla según el modo"""
        t = self._value
        
        if self.blend_mode == "linear":
            return t
        elif self.blend_mode == "smooth":
            return t * t * (3 - 2 * t)
        elif self.blend_mode == "ease_in":
            return t * t
        elif self.blend_mode == "ease_out":
            return 1 - (1 - t) * (1 - t)
        elif self.blend_mode == "ease_in_out":
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        
        return t
        
    def apply_to(self, value_a: Any, value_b: Any) -> Any:
        """Mezcla entre dos valores"""
        factor = self.calculate_blend_factor()
        
        if isinstance(value_a, np.ndarray) and isinstance(value_b, np.ndarray):
            return value_a * (1 - factor) + value_b * factor
        elif isinstance(value_a, (int, float)) and isinstance(value_b, (int, float)):
            return value_a * (1 - factor) + value_b * factor
        else:
            # Para otros tipos, devuelve uno u otro según el factor
            return value_b if factor > 0.5 else value_a
            
    def interpolate(self, other: 'BlendAmount', factor: float) -> 'BlendAmount':
        """Interpola entre dos blend amounts"""
        factor = max(0.0, min(1.0, factor))
        new_value = self._value * (1 - factor) + other._value * factor
        result = BlendAmount(new_value)
        result.blend_mode = self.blend_mode if factor < 0.5 else other.blend_mode
        return result


class VectorAmount:
    """Amount vectorial para magnitudes con dirección"""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x_amount = LinearAmount(x, -10.0, 10.0)
        self.y_amount = LinearAmount(y, -10.0, 10.0)
        self.z_amount = LinearAmount(z, -10.0, 10.0)
        
    @property
    def vector(self) -> np.ndarray:
        """Obtiene el vector de amounts"""
        return np.array([
            self.x_amount.value,
            self.y_amount.value,
            self.z_amount.value
        ])
        
    @property
    def magnitude(self) -> float:
        """Obtiene la magnitud del vector"""
        return np.linalg.norm(self.vector)
        
    @property
    def normalized_vector(self) -> np.ndarray:
        """Obtiene el vector normalizado"""
        mag = self.magnitude
        if mag > 0:
            return self.vector / mag
        return np.zeros(3)
        
    def set_from_vector(self, vector: np.ndarray):
        """Establece los valores desde un vector"""
        if len(vector) >= 3:
            self.x_amount.value = vector[0]
            self.y_amount.value = vector[1]
            self.z_amount.value = vector[2]
            
    def set_from_spherical(self, radius: float, theta: float, phi: float):
        """Establece valores desde coordenadas esféricas"""
        x = radius * np.sin(phi) * np.cos(theta)
        y = radius * np.sin(phi) * np.sin(theta)
        z = radius * np.cos(phi)
        self.set_from_vector([x, y, z])
        
    def apply_to(self, position: np.ndarray) -> np.ndarray:
        """Aplica el vector amount a una posición"""
        return position + self.vector
        
    def interpolate(self, other: 'VectorAmount', factor: float) -> 'VectorAmount':
        """Interpola entre dos vector amounts"""
        result = VectorAmount()
        result.x_amount = self.x_amount.interpolate(other.x_amount, factor)
        result.y_amount = self.y_amount.interpolate(other.y_amount, factor)
        result.z_amount = self.z_amount.interpolate(other.z_amount, factor)
        return result
        
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            'x': self.x_amount.to_dict(),
            'y': self.y_amount.to_dict(),
            'z': self.z_amount.to_dict(),
            'magnitude': self.magnitude,
            'vector': self.vector.tolist()
        }