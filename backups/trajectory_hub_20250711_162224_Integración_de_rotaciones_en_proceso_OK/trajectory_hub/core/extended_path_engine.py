"""
extended_path_engine.py - Motor de trayectorias extendido (versión básica temporal)
"""
import numpy as np
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
import logging

# Verificar disponibilidad de Numba para optimización
try:
    import numba
    _NUMBA_AVAILABLE = True
except ImportError:
    _NUMBA_AVAILABLE = False

# Variables de disponibilidad para diferentes módulos
_BEHAVIORS_AVAILABLE = True  # Los comportamientos básicos siempre están disponibles
_FORMATIONS_AVAILABLE = True  # Las formaciones básicas siempre están disponibles
_DEFORMATIONS_AVAILABLE = True  # Las deformaciones básicas siempre están disponibles

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

@dataclass
class PathPoint:
    """Punto en una trayectoria"""
    position: np.ndarray
    time: float
    velocity: Optional[np.ndarray] = None

class ExtendedPathEngine:
    """Motor de trayectorias extendido - versión básica"""
    
    def __init__(self):
        self.paths = {}
        self.active_sources = {}
        
    def create_path(self, path_id: str, points: List[PathPoint]):
        """Crear una nueva trayectoria"""
        self.paths[path_id] = points
        
    def get_position_at_time(self, path_id: str, time: float) -> np.ndarray:
        """Obtener posición en un tiempo específico"""
        if path_id not in self.paths:
            return np.array([0, 0, 0])
            
        points = self.paths[path_id]
        if not points:
            return np.array([0, 0, 0])
            
        # Interpolación simple entre puntos
        if len(points) == 1:
            return points[0].position
            
        # Encontrar puntos para interpolar
        for i in range(len(points) - 1):
            if points[i].time <= time <= points[i + 1].time:
                t = (time - points[i].time) / (points[i + 1].time - points[i].time)
                return points[i].position + t * (points[i + 1].position - points[i].position)
                
        # Si el tiempo está fuera del rango, usar el punto más cercano
        if time < points[0].time:
            return points[0].position
        else:
            return points[-1].position

# Clases adicionales que pueden ser importadas
class TrajectorySystem:
    """Sistema de trayectorias básico"""
    
    def __init__(self):
        self.engine = ExtendedPathEngine()
        
    def create_circular_path(self, radius: float = 5.0, duration: float = 10.0):
        """Crear trayectoria circular"""
        points = []
        num_points = 100
        
        for i in range(num_points):
            t = i / (num_points - 1) * duration
            angle = 2 * np.pi * t / duration
            pos = np.array([
                radius * np.cos(angle),
                radius * np.sin(angle),
                0
            ])
            points.append(PathPoint(pos, t))
            
        return points

class PathGenerator:
    """Generador de trayectorias"""
    
    @staticmethod
    def generate_spiral(radius: float = 5.0, height: float = 3.0, turns: int = 3, duration: float = 10.0):
        """Generar espiral"""
        points = []
        num_points = 100
        
        for i in range(num_points):
            t = i / (num_points - 1) * duration
            progress = t / duration
            angle = 2 * np.pi * turns * progress
            r = radius * (1 - 0.5 * progress)
            
            pos = np.array([
                r * np.cos(angle),
                r * np.sin(angle),
                height * progress
            ])
            points.append(PathPoint(pos, t))
            
        return points
        
    @staticmethod
    def generate_lissajous(a: float = 3, b: float = 2, delta: float = np.pi/2, 
                          scale: float = 5.0, duration: float = 10.0):
        """Generar curva de Lissajous"""
        points = []
        num_points = 100
        
        for i in range(num_points):
            t = i / (num_points - 1) * duration
            angle = 2 * np.pi * t / duration
            
            pos = np.array([
                scale * np.sin(a * angle + delta),
                scale * np.sin(b * angle),
                0
            ])
            points.append(PathPoint(pos, t))
            
        return points

# Funciones de utilidad
def interpolate_position(pos1: np.ndarray, pos2: np.ndarray, t: float) -> np.ndarray:
    """Interpolar entre dos posiciones"""
    return pos1 + t * (pos2 - pos1)

def calculate_velocity(pos1: np.ndarray, pos2: np.ndarray, dt: float) -> np.ndarray:
    """Calcular velocidad entre dos puntos"""
    if dt == 0:
        return np.array([0, 0, 0])
    return (pos2 - pos1) / dt

# Exportar clases principales
__all__ = [
    'ExtendedPathEngine',
    'TrajectorySystem', 
    'PathGenerator',
    'PathPoint',
    'interpolate_position',
    'calculate_velocity'
]

# Clases adicionales requeridas por enhanced_trajectory_engine
@dataclass
class BoidParams:
    """Parámetros para comportamiento de bandada (boids)"""
    separation_distance: float = 2.0
    alignment_radius: float = 5.0
    cohesion_radius: float = 8.0
    separation_weight: float = 1.5
    alignment_weight: float = 1.0
    cohesion_weight: float = 1.0
    max_speed: float = 2.0
    max_force: float = 0.3

@dataclass
class SourceInfo:
    """Información básica de una fuente de audio"""
    id: str
    name: str = ""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    orientation: np.ndarray = field(default_factory=lambda: np.zeros(3))
    aperture: float = 90.0  # grados
    gain: float = 1.0
    mute: bool = False
    solo: bool = False
    color: str = "#FFFFFF"
    group_id: Optional[str] = None
    
    def __post_init__(self):
        """Validar datos después de inicialización"""
        if isinstance(self.position, (list, tuple)):
            self.position = np.array(self.position, dtype=float)
        if isinstance(self.orientation, (list, tuple)):
            self.orientation = np.array(self.orientation, dtype=float)
        
        # Asegurar que son arrays 3D
        if self.position.size != 3:
            self.position = np.zeros(3)
        if self.orientation.size != 3:
            self.orientation = np.zeros(3)
            
        # Validar rangos
        self.aperture = max(0, min(180, self.aperture))
        self.gain = max(0, self.gain)

@dataclass
class MacroInfo:
    """Información de un macro (grupo de fuentes)"""
    id: str
    name: str = ""
    source_ids: List[str] = field(default_factory=list)
    behavior_type: str = "flock"
    formation_type: str = "circle"
    formation_spacing: float = 2.0
    center_position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    enabled: bool = True
    
    def __post_init__(self):
        if isinstance(self.center_position, (list, tuple)):
            self.center_position = np.array(self.center_position, dtype=float)
        if self.center_position.size != 3:
            self.center_position = np.zeros(3)

@dataclass  
class TrajectoryState:
    """Estado actual de una trayectoria"""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    acceleration: np.ndarray = field(default_factory=lambda: np.zeros(3))
    time: float = 0.0
    phase: float = 0.0
    
    def __post_init__(self):
        for attr in ['position', 'velocity', 'acceleration']:
            value = getattr(self, attr)
            if isinstance(value, (list, tuple)):
                setattr(self, attr, np.array(value, dtype=float))
            elif not isinstance(value, np.ndarray):
                setattr(self, attr, np.zeros(3))
            elif value.size != 3:
                setattr(self, attr, np.zeros(3))

class TrajectoryManager:
    """Gestor de trayectorias básico"""
    
    def __init__(self):
        self.sources: Dict[str, SourceInfo] = {}
        self.macros: Dict[str, MacroInfo] = {}
        self.trajectories: Dict[str, TrajectoryState] = {}
        
    def add_source(self, source_info: SourceInfo):
        """Añadir fuente"""
        self.sources[source_info.id] = source_info
        self.trajectories[source_info.id] = TrajectoryState()
        
    def add_macro(self, macro_info: MacroInfo):
        """Añadir macro"""
        self.macros[macro_info.id] = macro_info
        
    def get_source(self, source_id: str) -> Optional[SourceInfo]:
        """Obtener información de fuente"""
        return self.sources.get(source_id)
        
    def get_macro(self, macro_id: str) -> Optional[MacroInfo]:
        """Obtener información de macro"""
        return self.macros.get(macro_id)
        
    def update_source_position(self, source_id: str, position: np.ndarray):
        """Actualizar posición de fuente"""
        if source_id in self.sources:
            self.sources[source_id].position = position.copy()
        if source_id in self.trajectories:
            self.trajectories[source_id].position = position.copy()

class MacroSource:
    """Clase que representa un macro (grupo de fuentes) como una entidad única"""
    
    def __init__(self, macro_id: str, name: str = "", behavior: str = "flock"):
        self.id = macro_id
        self.name = name or f"Macro_{macro_id}"
        self.behavior_name = behavior
        self.behavior = None  # Se asignará después
        
        # Fuentes que componen el macro
        self.source_ids: set = set()
        self.center_source_id: Optional[str] = None
        
        # Configuración de formación
        self.formation_type = "circle"
        self.formation_spacing = 2.0
        self.formation_offsets: Dict[str, np.ndarray] = {}
        
        # Trayectorias
        self.has_trajectory = False
        self.base_trajectory_func: Optional[Callable[[float], np.ndarray]] = None
        self.base_orientation_func: Optional[Callable[[float], np.ndarray]] = None
        self.individual_trajectories: Dict[str, str] = {}
        
        # Deformación
        self.deformation_enabled = False
        self.allow_different_trajectories = True
        
        # Estado
        self.enabled = True
        self.time_offset = 0.0
        
    def add_source(self, source_id: str, offset: Optional[np.ndarray] = None):
        """Añadir fuente al macro"""
        self.source_ids.add(source_id)
        if offset is not None:
            self.formation_offsets[source_id] = offset.copy()
            
        # Si es la primera fuente, hacerla el centro
        if self.center_source_id is None:
            self.center_source_id = source_id
            
    def remove_source(self, source_id: str):
        """Remover fuente del macro"""
        self.source_ids.discard(source_id)
        self.formation_offsets.pop(source_id, None)
        
        # Si era el centro, elegir nuevo centro
        if self.center_source_id == source_id:
            self.center_source_id = next(iter(self.source_ids), None)
            
    def get_center_position(self, source_positions: Dict[str, np.ndarray]) -> np.ndarray:
        """Obtener posición del centro del macro"""
        if self.center_source_id and self.center_source_id in source_positions:
            return source_positions[self.center_source_id].copy()
            
        # Si no hay centro definido, calcular promedio
        positions = [source_positions[sid] for sid in self.source_ids if sid in source_positions]
        if positions:
            return np.mean(positions, axis=0)
        else:
            return np.zeros(3)
            
    def set_trajectory(self, trajectory_func: Callable[[float], np.ndarray], 
                      orientation_func: Optional[Callable[[float], np.ndarray]] = None):
        """Establecer trayectoria del macro"""
        self.base_trajectory_func = trajectory_func
        self.base_orientation_func = orientation_func
        self.has_trajectory = True
        
    def clear_trajectory(self):
        """Limpiar trayectoria del macro"""
        self.base_trajectory_func = None
        self.base_orientation_func = None
        self.has_trajectory = False
        
    def set_individual_trajectory(self, source_id: str, trajectory_type: str):
        """Establecer trayectoria individual para una fuente"""
        if source_id in self.source_ids:
            self.individual_trajectories[source_id] = trajectory_type
            
    def get_source_count(self) -> int:
        """Obtener número de fuentes en el macro"""
        return len(self.source_ids)
        
    def is_empty(self) -> bool:
        """Verificar si el macro está vacío"""
        return len(self.source_ids) == 0
        
    def __repr__(self) -> str:
        return f"MacroSource(id='{self.id}', name='{self.name}', sources={len(self.source_ids)})"

class SimpleMotionSystem:
    """Sistema básico de movimiento para compatibilidad"""
    
    def __init__(self):
        self.sources: Dict[str, SourceInfo] = {}
        self.macros: Dict[str, MacroSource] = {}
        self.time = 0.0
        
    def add_source(self, source_info: SourceInfo) -> str:
        """Añadir fuente al sistema"""
        self.sources[source_info.id] = source_info
        return source_info.id
        
    def create_macro(self, name: str, source_ids: List[str], behavior: str = "flock") -> str:
        """Crear macro con fuentes existentes"""
        macro_id = f"macro_{len(self.macros)}"
        macro = MacroSource(macro_id, name, behavior)
        
        for source_id in source_ids:
            if source_id in self.sources:
                macro.add_source(source_id)
                
        self.macros[macro_id] = macro
        return macro_id
        
    def get_macro(self, macro_id: str) -> Optional[MacroSource]:
        """Obtener macro por ID"""
        return self.macros.get(macro_id)
        
    def update_time(self, dt: float):
        """Actualizar tiempo del sistema"""
        self.time += dt
        
    def step(self):
        """Ejecutar un paso de simulación"""
        self.update_time(1.0/60.0)  # Asumir 60 FPS
        
        # Aquí iría la lógica de actualización de posiciones
        # Por ahora, solo mantener las posiciones actuales
        
        return {
            'time': self.time,
            'source_count': len(self.sources),
            'macro_count': len(self.macros)
        }

@dataclass 
class FlockingSystem:
    """Sistema de bandada básico"""
    params: BoidParams
    
    def __init__(self, params: Optional[BoidParams] = None):
        self.params = params or BoidParams()
        
    def calculate_separation(self, position: np.ndarray, neighbors: List[np.ndarray]) -> np.ndarray:
        """Calcular fuerza de separación"""
        force = np.zeros(3)
        count = 0
        
        for neighbor in neighbors:
            distance = np.linalg.norm(position - neighbor)
            if 0 < distance < self.params.separation_distance:
                diff = position - neighbor
                diff = diff / distance  # Normalizar
                force += diff
                count += 1
                
        if count > 0:
            force = force / count
            
        return force * self.params.separation_weight
    
    def calculate_alignment(self, velocity: np.ndarray, neighbor_velocities: List[np.ndarray]) -> np.ndarray:
        """Calcular fuerza de alineación"""
        if not neighbor_velocities:
            return np.zeros(3)
            
        avg_velocity = np.mean(neighbor_velocities, axis=0)
        force = avg_velocity - velocity
        
        return force * self.params.alignment_weight
    
    def calculate_cohesion(self, position: np.ndarray, neighbors: List[np.ndarray]) -> np.ndarray:
        """Calcular fuerza de cohesión"""
        if not neighbors:
            return np.zeros(3)
            
        center = np.mean(neighbors, axis=0)
        force = center - position
        
        return force * self.params.cohesion_weight

class FormationPattern:
    """Patrones de formación básicos"""
    
    @staticmethod
    def circle(num_points: int, radius: float = 5.0, center: np.ndarray = None) -> List[np.ndarray]:
        """Generar formación circular"""
        if center is None:
            center = np.array([0, 0, 0])
            
        points = []
        for i in range(num_points):
            angle = 2 * np.pi * i / num_points
            point = center + np.array([
                radius * np.cos(angle),
                radius * np.sin(angle),
                0
            ])
            points.append(point)
            
        return points
    
    @staticmethod
    def line(num_points: int, spacing: float = 2.0, direction: np.ndarray = None) -> List[np.ndarray]:
        """Generar formación en línea"""
        if direction is None:
            direction = np.array([1, 0, 0])
            
        points = []
        start = -(num_points - 1) * spacing / 2
        
        for i in range(num_points):
            offset = start + i * spacing
            point = offset * direction
            points.append(point)
            
        return points
    
    @staticmethod
    def grid(num_points: int, spacing: float = 2.0) -> List[np.ndarray]:
        """Generar formación en grid"""
        side = int(np.ceil(np.sqrt(num_points)))
        points = []
        
        for i in range(num_points):
            row = i // side
            col = i % side
            point = np.array([
                col * spacing - (side - 1) * spacing / 2,
                row * spacing - (side - 1) * spacing / 2,
                0
            ])
            points.append(point)
            
        return points

# Funciones de utilidad adicionales
def clamp_magnitude(vector: np.ndarray, max_magnitude: float) -> np.ndarray:
    """Limitar la magnitud de un vector"""
    magnitude = np.linalg.norm(vector)
    if magnitude > max_magnitude:
        return vector * (max_magnitude / magnitude)
    return vector

def normalize_safe(vector: np.ndarray) -> np.ndarray:
    """Normalizar vector con protección contra división por cero"""
    magnitude = np.linalg.norm(vector)
    if magnitude > 1e-8:
        return vector / magnitude
    return np.array([1, 0, 0])  # Vector por defecto

# Actualizar exportaciones
__all__ = [
    'ExtendedPathEngine',
    'TrajectorySystem', 
    'PathGenerator',
    'PathPoint',
    'interpolate_position',
    'calculate_velocity',
    'BoidParams',
    'SourceInfo',
    'MacroInfo',
    'TrajectoryState',
    'TrajectoryManager',
    'MacroSource',
    'SimpleMotionSystem',
    'FlockingSystem',
    'FormationPattern',
    'clamp_magnitude',
    'normalize_safe',
    '_NUMBA_AVAILABLE',
    '_BEHAVIORS_AVAILABLE',
    '_FORMATIONS_AVAILABLE',
    '_DEFORMATIONS_AVAILABLE'
]