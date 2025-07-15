"""
Sistema unificado de Amount/Magnitude para controlar amplitudes y cantidades
en el sistema de trayectorias.
"""
import numpy as np
from typing import Optional, Union, Dict, Any
from abc import ABC, abstractmethod
from enum import Enum


class AmountType(Enum):
    """Tipos de amount disponibles"""
    LINEAR = "linear"          # Magnitud lineal (distancia)
    ANGULAR = "angular"        # Magnitud angular (rotación)
    SCALE = "scale"           # Factor de escala
    INTENSITY = "intensity"   # Intensidad general
    SPEED = "speed"           # Modificador de velocidad
    FORCE = "force"           # Fuerza/Atracción
    WAVE = "wave"             # Amplitud de onda
    NOISE = "noise"           # Cantidad de ruido
    BLEND = "blend"           # Mezcla entre estados


class AmountUnit(Enum):
    """Unidades de medida para amounts"""
    NORMALIZED = "normalized"  # 0.0 a 1.0
    PERCENTAGE = "percentage"  # 0 a 100
    METERS = "meters"         # Distancia en metros
    DEGREES = "degrees"       # Ángulos en grados
    RADIANS = "radians"       # Ángulos en radianes
    MULTIPLIER = "multiplier" # Factor multiplicador
    DECIBELS = "decibels"     # Decibelios
    HERTZ = "hertz"           # Frecuencia


class Amount(ABC):
    """Clase base abstracta para todos los tipos de amount"""
    
    def __init__(self, 
                 value: float = 1.0,
                 min_value: float = 0.0,
                 max_value: float = 1.0,
                 unit: AmountUnit = AmountUnit.NORMALIZED,
                 amount_type: AmountType = AmountType.INTENSITY):
        """
        Inicializa un Amount
        
        Args:
            value: Valor inicial
            min_value: Valor mínimo permitido
            max_value: Valor máximo permitido
            unit: Unidad de medida
            amount_type: Tipo de amount
        """
        self._amount_type = amount_type
        self._unit = unit
        self._min_value = min_value
        self._max_value = max_value
        self._value = self._clamp(value)
        
        # Metadatos opcionales
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.interpolation_type: str = "linear"  # linear, smooth, exponential
        
    def _clamp(self, value: float) -> float:
        """Limita el valor al rango permitido"""
        return max(self._min_value, min(self._max_value, value))
        
    @property
    def value(self) -> float:
        """Obtiene el valor actual"""
        return self._value
        
    @value.setter
    def value(self, new_value: float):
        """Establece un nuevo valor (con clamping)"""
        self._value = self._clamp(new_value)
        
    @property
    def normalized(self) -> float:
        """Obtiene el valor normalizado (0.0 a 1.0)"""
        if self._max_value == self._min_value:
            return 0.0
        return (self._value - self._min_value) / (self._max_value - self._min_value)
        
    @normalized.setter
    def normalized(self, norm_value: float):
        """Establece el valor desde un valor normalizado"""
        norm_clamped = max(0.0, min(1.0, norm_value))
        self._value = self._min_value + norm_clamped * (self._max_value - self._min_value)
        
    @abstractmethod
    def apply_to(self, target: Any) -> Any:
        """Aplica este amount a un objetivo"""
        pass
        
    @abstractmethod
    def interpolate(self, other: 'Amount', factor: float) -> 'Amount':
        """Interpola entre este amount y otro"""
        pass
        
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización"""
        return {
            'type': self._amount_type.value,
            'unit': self._unit.value,
            'value': self._value,
            'min_value': self._min_value,
            'max_value': self._max_value,
            'normalized': self.normalized,
            'name': self.name,
            'description': self.description,
            'interpolation_type': self.interpolation_type
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Amount':
        """Crea un Amount desde un diccionario"""
        # Implementación específica en subclases
        raise NotImplementedError


class LinearAmount(Amount):
    """Amount para magnitudes lineales (distancias, desplazamientos)"""
    
    def __init__(self, 
                 value: float = 1.0,
                 min_value: float = 0.0,
                 max_value: float = 10.0,
                 unit: AmountUnit = AmountUnit.METERS):
        super().__init__(value, min_value, max_value, unit, AmountType.LINEAR)
        
    def apply_to(self, position: np.ndarray) -> np.ndarray:
        """Aplica la magnitud a una posición"""
        # Escala la posición por el valor
        return position * self._value
        
    def interpolate(self, other: 'LinearAmount', factor: float) -> 'LinearAmount':
        """Interpola entre dos amounts lineales"""
        factor = max(0.0, min(1.0, factor))
        new_value = self._value * (1 - factor) + other._value * factor
        return LinearAmount(new_value, self._min_value, self._max_value, self._unit)


class AngularAmount(Amount):
    """Amount para magnitudes angulares (rotaciones)"""
    
    def __init__(self, 
                 value: float = 0.0,
                 min_value: float = -360.0,
                 max_value: float = 360.0,
                 unit: AmountUnit = AmountUnit.DEGREES):
        super().__init__(value, min_value, max_value, unit, AmountType.ANGULAR)
        
    @property
    def radians(self) -> float:
        """Obtiene el valor en radianes"""
        if self._unit == AmountUnit.RADIANS:
            return self._value
        elif self._unit == AmountUnit.DEGREES:
            return np.radians(self._value)
        else:
            # Para normalized, asumimos que el rango completo es 2π
            return self.normalized * 2 * np.pi
            
    def apply_to(self, angle: float) -> float:
        """Aplica la magnitud a un ángulo"""
        return angle + self.radians
        
    def interpolate(self, other: 'AngularAmount', factor: float) -> 'AngularAmount':
        """Interpola entre dos amounts angulares"""
        factor = max(0.0, min(1.0, factor))
        # Interpolación angular considerando el camino más corto
        diff = other._value - self._value
        if self._unit == AmountUnit.DEGREES:
            if diff > 180:
                diff -= 360
            elif diff < -180:
                diff += 360
        new_value = self._value + diff * factor
        return AngularAmount(new_value, self._min_value, self._max_value, self._unit)


class ScaleAmount(Amount):
    """Amount para factores de escala"""
    
    def __init__(self, 
                 value: float = 1.0,
                 min_value: float = 0.1,
                 max_value: float = 10.0):
        super().__init__(value, min_value, max_value, 
                        AmountUnit.MULTIPLIER, AmountType.SCALE)
        
    def apply_to(self, size: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Aplica el factor de escala"""
        return size * self._value
        
    def interpolate(self, other: 'ScaleAmount', factor: float) -> 'ScaleAmount':
        """Interpola entre dos amounts de escala"""
        factor = max(0.0, min(1.0, factor))
        # Interpolación logarítmica para escalas
        if self.interpolation_type == "exponential":
            log_start = np.log(self._value)
            log_end = np.log(other._value)
            log_value = log_start * (1 - factor) + log_end * factor
            new_value = np.exp(log_value)
        else:
            new_value = self._value * (1 - factor) + other._value * factor
        return ScaleAmount(new_value, self._min_value, self._max_value)


class IntensityAmount(Amount):
    """Amount genérico para intensidades (0.0 a 1.0)"""
    
    def __init__(self, value: float = 1.0):
        super().__init__(value, 0.0, 1.0, 
                        AmountUnit.NORMALIZED, AmountType.INTENSITY)
        
    def apply_to(self, value: float) -> float:
        """Aplica la intensidad como multiplicador"""
        return value * self._value
        
    def interpolate(self, other: 'IntensityAmount', factor: float) -> 'IntensityAmount':
        """Interpola entre dos intensidades"""
        factor = max(0.0, min(1.0, factor))
        if self.interpolation_type == "smooth":
            # Interpolación suave usando coseno
            factor = 0.5 * (1 - np.cos(factor * np.pi))
        new_value = self._value * (1 - factor) + other._value * factor
        return IntensityAmount(new_value)


class CompositeAmount:
    """Contenedor para múltiples amounts que trabajan juntos"""
    
    def __init__(self):
        self.amounts: Dict[str, Amount] = {}
        
    def add(self, name: str, amount: Amount):
        """Añade un amount al composite"""
        amount.name = name
        self.amounts[name] = amount
        
    def get(self, name: str) -> Optional[Amount]:
        """Obtiene un amount por nombre"""
        return self.amounts.get(name)
        
    def apply_all(self, target: Any) -> Any:
        """Aplica todos los amounts al objetivo"""
        result = target
        for amount in self.amounts.values():
            result = amount.apply_to(result)
        return result
        
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            name: amount.to_dict() 
            for name, amount in self.amounts.items()
        }
        
    def interpolate(self, other: 'CompositeAmount', factor: float) -> 'CompositeAmount':
        """Interpola entre dos composites"""
        result = CompositeAmount()
        for name, amount in self.amounts.items():
            if name in other.amounts:
                interpolated = amount.interpolate(other.amounts[name], factor)
                result.add(name, interpolated)
        return result


# Factory functions para crear amounts comunes
def create_rotation_amount(magnitude: float = 1.0) -> IntensityAmount:
    """Crea un amount para controlar magnitud de rotación"""
    amount = IntensityAmount(magnitude)
    amount.name = "rotation_magnitude"
    amount.description = "Controls rotation amplitude"
    return amount


def create_speed_amount(multiplier: float = 1.0) -> ScaleAmount:
    """Crea un amount para modificar velocidad"""
    amount = ScaleAmount(multiplier, 0.1, 5.0)
    amount.name = "speed_multiplier" 
    amount.description = "Speed modification factor"
    return amount


def create_distance_amount(meters: float = 1.0) -> LinearAmount:
    """Crea un amount para distancias"""
    amount = LinearAmount(meters, 0.0, 100.0, AmountUnit.METERS)
    amount.name = "distance"
    amount.description = "Distance in meters"
    return amount