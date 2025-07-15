"""
enhanced_trajectory_engine.py - Motor de trayectorias con sistema de componentes completo
Evolución de extended_path_engine.py que mantiene compatibilidad e integra motion_components
"""
from __future__ import annotations
import numpy as np


try:
    from rotation_system import MacroRotation, TrajectoryRotation, RotationPresets, RotationPattern
except ImportError:
    print('⚠️ rotation_system.py no encontrado')
    MacroRotation = None
import logging
import time
from typing import Dict, List, Optional, Callable, Set, Tuple, Any
from dataclasses import dataclass, field

# Importar el sistema de componentes
from trajectory_hub.core.motion_components import (
    SourceMotion, TrajectoryMovementMode, TrajectoryDisplacementMode,
    OrientationModulation, IndividualTrajectory, TrajectoryTransform,
    MacroTrajectory, create_complex_movement, MotionState,
    AdvancedOrientationModulation
)
from trajectory_hub.core.trajectory_deformers import (
    CompositeDeformer, ForceFieldDeformation, WaveDeformation,
    ChaoticDeformation, GestureDeformation, BlendMode
)
# Mantener compatibilidad con el sistema anterior
from trajectory_hub.core.extended_path_engine import (
    BoidParams, SourceInfo, MacroSource,
    _NUMBA_AVAILABLE, _BEHAVIORS_AVAILABLE
)

logger = logging.getLogger(__name__)


@dataclass
class EnhancedMacroSource(MacroSource):
    """Versión mejorada de MacroSource con soporte para el nuevo sistema"""

    # Campos base heredados de MacroSource
    name: str = ""
    behavior_name: str = "flock"

    # Componente de trayectoria macro
    trajectory_component: Optional[MacroTrajectory] = None
    
    # Configuración de trayectorias individuales
    individual_trajectories: Dict[int, str] = field(default_factory=dict)  # source_id: shape_type
    allow_different_trajectories: bool = False
    
    # Estado de concentración
    concentration_active: bool = False
    concentration_point: np.ndarray = field(default_factory=lambda: np.zeros(3))
    concentration_duration: float = 1.0
    
    # Deformador
    deformer: Optional[CompositeDeformer] = None
    deformation_enabled: bool = False

    def __post_init__(self):
        """Inicializar la clase padre MacroSource y configurar componentes"""
        # Inicializar los atributos de MacroSource de forma segura
        try:
            # Usar los valores por defecto si no están establecidos
            macro_id = getattr(self, 'id', f"macro_{id(self)}")
            name = getattr(self, 'name', f"Macro_{macro_id}")
            behavior = getattr(self, 'behavior_name', 'flock')
            
            # Llamar al constructor padre
            super().__init__(macro_id, name, behavior)
        except Exception as e:
            # Si hay algún problema, inicializar manualmente los atributos críticos
            logger.warning(f"Error en __post_init__: {e}. Inicializando manualmente.")
            if not hasattr(self, 'source_ids'):
                self.source_ids = set()
            if not hasattr(self, 'behavior'):
                self.behavior = None
                
        # Asegurar que trajectory_component se inicialice
        if self.trajectory_component is None:
            from trajectory_hub.core.motion_components import MacroTrajectory
            self.trajectory_component = MacroTrajectory()


class EnhancedTrajectoryEngine:
    """
    Motor de trayectorias mejorado que integra el sistema de componentes
    Mantiene compatibilidad con la API anterior mientras añade nuevas capacidades
    """
    
    def __init__(self, max_sources: int = 64, fps: int = 60, 
                 params: Optional[BoidParams] = None,
                 use_legacy_mode: bool = False,
                 enable_modulator: bool = True):
        """
        Parameters
        ----------
        max_sources : int
            Número máximo de fuentes
        fps : int
            Frames por segundo
        params : BoidParams
            Parámetros de comportamiento boids
        use_legacy_mode : bool
            Si True, usa el comportamiento anterior (para compatibilidad)
        enable_modulator : bool
            Si True, habilita el sistema de modulación de orientación
        """
        self.max_sources = max_sources
        self.fps = fps
        self.dt = 1.0 / fps
        self.params = params or BoidParams()
        self.use_legacy_mode = use_legacy_mode
        
        # Sistema de componentes nuevo
        self._source_motions: Dict[int, SourceMotion] = {}
        
        # Información de fuentes y macros (compatible con versión anterior)
        self._source_info: Dict[int, SourceInfo] = {}
        self._macros: Dict[str, EnhancedMacroSource] = {}
        
        # Estado interno
        self._time = 0.0
        self._frame_count = 0
        
        # Arrays para compatibilidad y optimización
        self._positions = np.zeros((max_sources, 3), dtype=np.float32)
        self._orientations = np.zeros((max_sources, 3), dtype=np.float32)
        self._apertures = np.ones(max_sources, dtype=np.float32) * 0.5
        
        # Sistema de deformadores global
        self.global_deformer = CompositeDeformer()

        # Deformadores por macro
        self._macro_deformers: Dict[str, CompositeDeformer] = {}
        
        # Sistema de modulación de orientación
        self.enable_modulator = enable_modulator
        self.orientation_modulators = {}  # Diccionario para guardar moduladores
        
        # Configuración global del modulador
        self.global_modulator_intensity = 1.0
        self.global_modulator_preset = None
        
        # Cache de últimas orientaciones enviadas
        self._last_orientations = {}
        self._orientation_update_threshold = 0.01
        
        # Cache de últimas aperturas enviadas
        self._last_apertures = {}
        self._aperture_update_threshold = 0.01  # Cambio mínimo para actualizar
        
        # Cache de últimas aperturas enviadas
        self._last_apertures = {}
        self._aperture_update_threshold = 0.01  # Cambio mínimo para actualizar  # radianes
        
        # OSC Bridge (se configura externamente)
        self.osc_bridge = None
        self._is_running = True

        logger.info(f"EnhancedTrajectoryEngine inicializado ({max_sources} fuentes @ {fps} fps)")

        # Diccionarios para tracking de cambios
        self._last_positions = {}
        self._last_orientations = {}
        self._last_apertures = {}
        self.time_paused = False
        # Sistema de rotación
        self.macro_rotations = {}
        self.trajectory_rotations = {}


    
    def create_source(self, source_id: int, name: Optional[str] = None) -> SourceMotion:
        """
        Crear una nueva fuente con sistema de componentes
        
        Parameters
        ----------
        source_id : int
            ID único de la fuente
        name : str, optional
            Nombre de la fuente
            
        Returns
        -------
        SourceMotion
            Objeto de movimiento creado
        """
        if source_id >= self.max_sources:
            raise ValueError(f"ID {source_id} excede el máximo de fuentes ({self.max_sources})")
            
        if source_id in self._source_motions:
            logger.warning(f"Fuente {source_id} ya existe, retornando existente")
            return self._source_motions[source_id]
            
        # Crear objeto de movimiento
        motion = SourceMotion(source_id)
        
        # Configurar posición inicial aleatoria
        angle = np.random.uniform(0, 2 * np.pi)
        radius = np.random.uniform(1, 3)
        motion.state.position = np.array([
            radius * np.cos(angle),
            radius * np.sin(angle),
            np.random.uniform(-0.5, 0.5)
        ])
        
        # Registrar en el sistema
        self._source_motions[source_id] = motion
        
        # CORRECCIÓN: Configurar componentes para respetar formaciones
        # Deshabilitar trayectorias individuales por defecto
        motion.components['individual_trajectory'].enabled = False
        motion.components['trajectory_transform'].enabled = False
        motion.components['macro_trajectory'].enabled = False
        motion.components['group_behavior'].enabled = False
        motion.components['environmental_forces'].enabled = False
        
        # Solo mantener orientación habilitada por defecto
        # motion.components['orientation_modulation'].enabled permanece True
        
        self._positions[source_id] = motion.state.position
        
        # Crear info para compatibilidad
        info = SourceInfo(
            id=str(source_id),
            name=name or f"Source_{source_id}",
            position=motion.state.position.copy()
        )
        self._source_info[source_id] = info
        
        # Crear modulador de orientación si está habilitado
        if self.enable_modulator:
            self.create_orientation_modulator(source_id)
        
        logger.info(f"Fuente {source_id} creada: {info.name}")
        return motion

    def create_orientation_modulator(self, source_id: int) -> Optional[AdvancedOrientationModulation]:
        """Crear modulador de orientación para una fuente"""
        if not self.enable_modulator:
            return None
            
        if source_id not in self._source_motions:
            logger.error(f"No se puede crear modulador para fuente inexistente {source_id}")
            return None
            
        # Crear modulador avanzado
        modulator = AdvancedOrientationModulation()
        modulator.source_id = source_id
        
        # Configurar con intensidad global
        modulator.intensity = self.global_modulator_intensity
        
        # Registrar
        self.orientation_modulators[source_id] = modulator
        
        logger.debug(f"Modulador de orientación creado para fuente {source_id}")
        return modulator
        return True

    def create_macro(
        self, 
        name: str, 
        source_count: int, 
        behavior: str = "flock",
        formation: str = "circle",
        spacing: float = 2.0,
        **kwargs
    ) -> str:
        # CORRECCIÓN: Flexibilidad para source_count
        if isinstance(source_count, list):
            actual_source_count = len(source_count)
        else:
            actual_source_count = source_count
        
        """
        Crear un macro (grupo de fuentes)
        
        Parameters
        ----------
        name : str
            Nombre del macro
        source_count : int
            Número de fuentes en el macro
        behavior : str
            Tipo de comportamiento (flock, rigid, orbit, etc.)
        formation : str
            Formación inicial (circle, line, grid, spiral)
        spacing : float
            Espaciado entre fuentes
            
        Returns
        -------
        str
            ID del macro creado
        """
        # Generar ID único
        macro_id = f"macro_{len(self._macros)}_{name.lower().replace(' ', '_')}"
        
        # Crear conjunto de fuentes
        source_ids = []
        start_id = len(self._source_motions)
        
        for i in range(actual_source_count):
            sid = start_id + i
            if sid < self.max_sources:
                self.create_source(sid, f"{name}_{i}")
                source_ids.append(sid)
        
        # Crear macro con los campos necesarios
        macro = EnhancedMacroSource()
        
        # Establecer campos base
        macro.id = macro_id
        macro.name = name
        macro.behavior_name = behavior
        
        # Establecer campos opcionales
        if 'allow_different_trajectories' in kwargs:
            macro.allow_different_trajectories = kwargs['allow_different_trajectories']
        
        # Añadir fuentes al macro
        for sid in source_ids:
            macro.add_source(sid)
            if sid in self._source_info:
                self._source_info[sid].macro_id = macro_id
                
        # Crear componente de trayectoria macro
        macro.trajectory_component = MacroTrajectory()
        
        # Aplicar formación inicial
        self._apply_formation(source_ids, formation, spacing)
        
        # Registrar macro
        self._macros[macro_id] = macro
        
        logger.info(f"Macro '{name}' creado con {len(source_ids)} fuentes")
        
        # Crear moduladores de orientación si está habilitado
        if self.enable_modulator:
            for i, sid in enumerate(source_ids):
                modulator = self.create_orientation_modulator(sid)
                if modulator:
                    # Desfase temporal para efecto orgánico
                    modulator.time_offset = i * 0.05
                
        # Si hay un preset global configurado, aplicarlo
        if self.global_modulator_preset:
            self.apply_orientation_preset(macro_id, self.global_modulator_preset)
            
        
        # Enviar creación del macro a Spat via OSC
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            try:
                # Crear el grupo en Spat
                self.osc_bridge.create_group(macro_id, name)
                
                # Añadir cada fuente al grupo
                for sid in macro.source_ids:
                    self.osc_bridge.add_source_to_group(sid, name)
                    
            except Exception as e:
                print(f"Error enviando macro a Spat: {e}")
        
        return macro_id

    def set_macro_concentration(self, macro_id: str, concentration_factor: float):
        """
        Establece el factor de concentración para un macro.
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        concentration_factor : float
            Factor de concentración (0=sin cambio, 1=máxima concentración)
        """
        import numpy as np
        
        if macro_id not in self._macros:
            print(f"⚠️ Macro {macro_id} no encontrado")
            return
            
        macro = self._macros[macro_id]
        macro.concentration_factor = concentration_factor
        
        if not macro.source_ids:
            return
        
        # Calcular centro del macro
        positions = []
        for sid in macro.source_ids:
            if sid in self._source_motions:
                motion = self._source_motions[sid]
                positions.append(motion.state.position.copy())
            elif sid < len(self._positions):
                positions.append(self._positions[sid].copy())
        
        if not positions:
            return
            
        center = np.mean(positions, axis=0)
        
        # Aplicar offset a cada fuente
        for i, sid in enumerate(macro.source_ids):
            if sid in self._source_motions:
                motion = self._source_motions[sid]
                
                # Vector desde la fuente hacia el centro
                direction = center - positions[i]
                
                # Aplicar factor
                motion.concentration_offset = direction * concentration_factor

    def _apply_formation(self, source_ids: List[int], formation: str, spacing: float):
        """Aplicar formación inicial a un conjunto de fuentes"""
        total = len(source_ids)
        
        if total == 0:
            return
            
        # Centro de la formación (alrededor del listener)
        center = np.array([0.0, 0.0, 0.0])
        
        for index, sid in enumerate(source_ids):
            if sid not in self._source_motions:
                continue
                
            motion = self._source_motions[sid]
            
            # Calcular posición según formación
            if formation == "circle":
                angle = (index / total) * 2 * np.pi
                x = center[0] + spacing * np.cos(angle)
                y = center[1] + spacing * np.sin(angle)
                z = center[2]
            elif formation == "line":
                # Línea horizontal centrada
                x = center[0] + (index - total/2) * spacing
                y = center[1]
                z = center[2]
                
            elif formation == "grid":
                # Grid cuadrado
                grid_size = int(np.ceil(np.sqrt(total)))
                row = index // grid_size
                col = index % grid_size
                x = center[0] + (col - grid_size/2) * spacing
                y = center[1] + (row - grid_size/2) * spacing
                z = center[2]
                
            elif formation == "spiral":
                # Espiral de Arquímedes con elevación 3D
                turns = 3  # Número de vueltas
                max_radius = spacing * np.sqrt(total)
                t = index / total
                angle = t * turns * 2 * np.pi
                radius = t * max_radius
                
                # Coordenadas x, y (espiral horizontal)
                x = center[0] + radius * np.cos(angle)
                y = center[1] + radius * np.sin(angle)
                
                # CORRECCIÓN QUIRÚRGICA: Elevación z variable
                z_height = spacing * 0.5  # Amplitud basada en spacing
                z_frequency = 2.0  # Frecuencia de oscilación
                z = center[2] + z_height * np.sin(z_frequency * angle)
                

            else:
                # Por defecto, círculo
                angle = (index / total) * 2 * np.pi
                x = center[0] + spacing * np.cos(angle)
                y = center[1] + spacing * np.sin(angle)
                z = center[2]
            
            # Establecer posición inicial
            position = np.array([x, y, z])
            motion.state.position = position
            motion.state.velocity = np.zeros(3)
            
            # Guardar posición de formación como base
            if 'individual_trajectory' in motion.components:
                motion.components['individual_trajectory'].base_position = position.copy()
            motion.state.acceleration = np.zeros(3)
            
                        # CORRECCIÓN: Actualizar también _positions array para consistencia
            self._positions[sid] = position
            
            # Actualizar source_info
            if sid in self._source_info:
                self._source_info[sid].position = position
                
            logger.debug(f"Fuente {sid} posicionada en {position} (formación {formation})")
        
        # ===== PARCHE DE DEBUG =====
        # DEBUG: Mostrar posiciones Z después de aplicar formación
        if formation == "spiral":
            print(f"\n🔍 DEBUG SPIRAL - Posiciones Z aplicadas:")
            z_values = []
            for idx, sid in enumerate(source_ids[:5]):  # Solo primeros 5
                if sid in self._source_motions:
                    pos = self._source_motions[sid].state.position
                    z_values.append(pos[2])
                    print(f"   Fuente {sid}: x={pos[0]:.3f}, y={pos[1]:.3f}, z={pos[2]:.6f}")
            
            if z_values:
                z_range = max(z_values) - min(z_values)
                print(f"   📊 Rango Z: {z_range:.6f}")
                if z_range > 0.001:
                    print(f"   ✅ CORRECTO: Fuentes tienen diferentes alturas Z")
                else:
                    print(f"   ❌ PROBLEMA: Todas las fuentes tienen la misma altura Z")
            
            # DEBUG adicional: Verificar _positions array
            print(f"\n🔍 DEBUG _positions array:")
            for idx, sid in enumerate(source_ids[:3]):
                if sid in self._positions:
                    pos_array = self._positions[sid]
                    print(f"   _positions[{sid}]: z={pos_array[2]:.6f}")
        # ===== FIN PARCHE DE DEBUG =====
    def set_individual_trajectory(
        self,
        source_id: int,
        shape: str,
        movement_mode: TrajectoryMovementMode = TrajectoryMovementMode.FIX,
        phase_factor: float = 1.0,
        initial_offset: float = 0.0,
        **params
    ):
        """Configurar trayectoria individual de una fuente"""
        if source_id not in self._source_motions:
            logger.error(f"Fuente {source_id} no existe")
            return
            
        motion = self._source_motions[source_id]
        traj = motion.components.get('individual_trajectory')
        
        if isinstance(traj, IndividualTrajectory):
            # Cambiar forma usando set_trajectory en lugar de _create_shape
            # Obtener posición actual si no se especificó centro
            if 'center' not in params and source_id < len(self._positions):
                current_pos = self._positions[source_id].copy()
                params['center'] = current_pos
                logger.info(f"Usando posición actual como centro: {current_pos}")
            
            traj.set_trajectory(shape, **params)
            traj.shape_type = shape
            
            # Configurar modo de movimiento
            # Configurar parámetros directamente
            traj.movement_mode = movement_mode
            traj.movement_speed = params.get('movement_speed', 1.0)
            traj.speed_factor = phase_factor
            traj.initial_offset = initial_offset
            traj.position_on_trajectory = initial_offset
            traj.movement_speed = params.get('movement_speed', 1.0)
            traj.speed_factor = phase_factor
            traj.initial_offset = initial_offset
            traj.position_on_trajectory = initial_offset
            traj.movement_speed = params.get('movement_speed', 1.0)
            traj.enabled = True
            
            logger.info(f"Trayectoria individual configurada: {shape} con modo {movement_mode.value}")

    def set_macro_trajectory(
        self,
        macro_id: str,
        trajectory_func: Callable[[float], np.ndarray],
        orientation_func: Optional[Callable[[float], np.ndarray]] = None,
        enable_deformation: bool = True
    ):
        """Establecer trayectoria de un macro completo"""
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no existe")
            return
            
        macro = self._macros[macro_id]
        
        # Configurar componente de trayectoria
        if macro.trajectory_component:
            macro.trajectory_component.set_trajectory(trajectory_func, orientation_func)
            macro.trajectory_component.enabled = True
            
        # Habilitar deformación si se solicita
        macro.deformation_enabled = enable_deformation
        
        logger.info(f"Trayectoria establecida para macro {macro_id}")

    def set_macro_speed(self, macro_id: str, speed: float):
        """
        Establecer velocidad global de un macro
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        speed : float
            Factor de velocidad (1.0 = normal, 2.0 = doble, 0.5 = mitad)
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no existe")
            return
            
        macro = self._macros[macro_id]
        
        # Establecer velocidad en el macro
        macro.trajectory_speed = speed
        
        # Aplicar velocidad a componente de trayectoria si existe
        if hasattr(macro, 'trajectory_component') and macro.trajectory_component:
            if hasattr(macro.trajectory_component, 'speed_factor'):
                macro.trajectory_component.speed_factor = speed
            if hasattr(macro.trajectory_component, 'movement_speed'):
                macro.trajectory_component.movement_speed = speed
        
        # Aplicar velocidad a todas las fuentes del macro si tienen trayectorias individuales
        if hasattr(macro, 'source_ids'):
            for source_id in macro.source_ids:
                if source_id in self._source_motions:
                    motion = self._source_motions[source_id]
                    if 'individual_trajectory' in motion.components:
                        traj = motion.components['individual_trajectory']
                        if hasattr(traj, 'movement_speed'):
                            traj.movement_speed = speed
                        if hasattr(traj, 'speed_factor'):
                            traj.speed_factor = speed
        
        logger.info(f"Velocidad {speed:.2f}x aplicada al macro {macro_id}")

    def set_macro_rotation(self, macro_name: str, pitch: float = 0.0, yaw: float = 0.0, roll: float = 0.0):
        """
        Aplicar rotación global a toda la formación del macro (como un trackball)
        
        Parameters
        ----------
        macro_name : str
            Nombre del macro
        pitch : float
            Rotación alrededor del eje X (radianes)
        yaw : float
            Rotación alrededor del eje Y (radianes)  
        roll : float
            Rotación alrededor del eje Z (radianes)
        """
        if macro_name not in self._macros:
            logger.error(f"Macro {macro_name} no existe")
            return
        
        # Calcular matriz de rotación
        # Rotación X (pitch)
        cx, sx = np.cos(pitch), np.sin(pitch)
        rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        
        # Rotación Y (yaw)
        cy, sy = np.cos(yaw), np.sin(yaw)
        ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        
        # Rotación Z (roll)
        cz, sz = np.cos(roll), np.sin(roll)
        rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
        
        # Matriz de rotación combinada
        rotation_matrix = rz @ ry @ rx
        
        # Guardar la rotación
        self.macro_rotations[macro_name] = rotation_matrix
        
        # Aplicar inmediatamente a todas las fuentes del macro
        self._apply_macro_rotation(macro_name)
        
        logger.info(f"Rotación aplicada al macro {macro_name}: pitch={pitch:.2f}, yaw={yaw:.2f}, roll={roll:.2f}")

    def set_trajectory_rotation(self, source_id: int, pitch: float, yaw: float, roll: float):
        """
        Establece la rotación manual de una trayectoria individual
        
        Parameters
        ----------
        source_id : int
            ID de la fuente
        pitch : float
            Rotación en X (radianes)
        yaw : float
            Rotación en Y (radianes)
        roll : float
            Rotación en Z (radianes)
        """
        if source_id not in self._source_motions:
            logger.warning(f"Fuente {source_id} no encontrada")
            return
        
        # Crear diccionario si no existe
        if not hasattr(self, 'trajectory_rotations'):
            self.trajectory_rotations = {}
        
        # Guardar rotación para aplicar en update
        self.trajectory_rotations[source_id] = {
            'pitch': pitch,
            'yaw': yaw,
            'roll': roll,
            'matrix': self._calculate_rotation_matrix(pitch, yaw, roll)
        }
        
        logger.info(f"Rotación manual establecida para trayectoria {source_id}: "
                   f"pitch={np.degrees(pitch):.1f}°, "
                   f"yaw={np.degrees(yaw):.1f}°, "
                   f"roll={np.degrees(roll):.1f}°")


    def _calculate_rotation_matrix(self, pitch: float, yaw: float, roll: float):
        """
        Calcular matriz de rotación 3x3 desde ángulos de Euler
        
        Parameters
        ----------
        pitch : float
            Rotación alrededor del eje X (radianes)
        yaw : float
            Rotación alrededor del eje Y (radianes)
        roll : float
            Rotación alrededor del eje Z (radianes)
            
        Returns
        -------
        np.ndarray
            Matriz de rotación 3x3
        """
        # Rotación X (pitch)
        cx, sx = np.cos(pitch), np.sin(pitch)
        rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        
        # Rotación Y (yaw)  
        cy, sy = np.cos(yaw), np.sin(yaw)
        ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        
        # Rotación Z (roll)
        cz, sz = np.cos(roll), np.sin(roll)
        rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
        
        # Matriz combinada: R = Rz * Ry * Rx
        return rz @ ry @ rx

    def set_individual_rotation(self, source_id: int, pitch: float = 0.0, yaw: float = 0.0, roll: float = 0.0):
        """
        Aplicar rotación a una trayectoria individual desde su centro
        
        Parameters
        ----------
        source_id : int
            ID de la fuente
        pitch : float
            Rotación alrededor del eje X (radianes)
        yaw : float
            Rotación alrededor del eje Y (radianes)  
        roll : float
            Rotación alrededor del eje Z (radianes)
        """
        # Simplemente redirigir a set_trajectory_rotation
        self.set_trajectory_rotation(source_id, pitch, yaw, roll)


    def rotate_individual_batch(self, source_ids: List[int], pitch: float = 0.0, yaw: float = 0.0, roll: float = 0.0):
        """
        Aplicar la misma rotación a múltiples trayectorias individuales
        
        Parameters
        ----------
        source_ids : List[int]
            Lista de IDs de fuentes
        pitch, yaw, roll : float
            Ángulos de rotación en radianes
        """
        for sid in source_ids:
            self.set_individual_rotation(sid, pitch, yaw, roll)
    
    def _apply_macro_rotation(self, macro_name: str):
        """Aplicar la rotación a todas las fuentes del macro"""
        if macro_name not in self._macros or macro_name not in self.macro_rotations:
            return
        
        macro = self._macros[macro_name]
        rotation_matrix = self.macro_rotations[macro_name]
        
        # Calcular el centro del macro
        positions = []
        for sid in macro.source_ids:
            if sid in self._positions:
                positions.append(self._positions[sid])
        
        if not positions:
            return
        
        center = np.mean(positions, axis=0)
        
        # Rotar cada fuente alrededor del centro
        for sid in macro.source_ids:
            if sid in self._source_motions:
                motion = self._source_motions[sid]
                
                # Posición relativa al centro
                rel_pos = motion.state.position - center
                
                # Aplicar rotación
                rotated_pos = rotation_matrix @ rel_pos
                
                # Nueva posición absoluta
                motion.state.position = center + rotated_pos
                self._positions[sid] = motion.state.position.copy()
    def set_mixed_trajectories(self, macro_id: str, shape_distribution: List[Tuple[str, float]]):
        """
        Asignar diferentes formas de trayectoria a las fuentes de un macro
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        shape_distribution : List[Tuple[str, float]]
            Lista de (forma, proporción) donde proporción suma 1.0
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no existe")
            return
            
        macro = self._macros[macro_id]
        macro.allow_different_trajectories = True
        
        source_list = list(macro.source_ids)
        total = len(source_list)
        
        # Asignar formas según distribución
        current_idx = 0
        for shape, proportion in shape_distribution:
            count = int(total * proportion)
            for i in range(count):
                if current_idx < total:
                    sid = source_list[current_idx]
                    macro.individual_trajectories[sid] = shape
                    
                    # Configurar la trayectoria individual
                    if sid in self._source_motions:
                        motion = self._source_motions[sid]
                        traj = motion.components.get('individual_trajectory')
                        if isinstance(traj, IndividualTrajectory):
                            traj.shape_type = shape
                            traj.set_trajectory(shape)
                            
                    current_idx += 1
                    
        logger.info(f"Trayectorias mixtas asignadas a macro {macro_id}")

    def apply_breathing(self, period: float = 5.0, amplitude: float = 1.0, 
                       macro_id: Optional[str] = None):
        """Aplicar efecto de respiración (expansión/contracción)"""
        if macro_id:
            if macro_id not in self._macro_deformers:
                self._macro_deformers[macro_id] = CompositeDeformer()
            deformer = self._macro_deformers[macro_id]
        else:
            deformer = self.global_deformer
            
        # Crear deformación de respiración
        breathing = WaveDeformation(
            wave_type="sine",
            frequency=1.0 / period,
            amplitude=amplitude,
            phase=0.0
        )
        breathing.scale_mode = True  # Modo escala
        
        deformer.add_deformation("breathing", breathing)
        logger.info(f"Respiración aplicada: período={period}s, amplitud={amplitude}")

    def apply_concentration(self, macro_id: str, point: np.ndarray, duration: float = 2.0):
        """
        Aplicar concentración temporal hacia un punto
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        point : np.ndarray
            Punto de concentración
        duration : float
            Duración de la transición
        """
        if macro_id not in self._macros:
            return
            
        macro = self._macros[macro_id]
        macro.concentration_active = True
        macro.concentration_point = point.copy()
        macro.concentration_duration = duration
        
        # Aplicar a cada fuente del macro
        start_time = self._time
        for sid in macro.source_ids:
            if sid not in self._source_motions:
                continue
                
            motion = self._source_motions[sid]
            transform = motion.components.get('trajectory_transform')
            
            if isinstance(transform, TrajectoryTransform):
                # Función de interpolación temporal
                initial_offset = transform.offset.copy() if isinstance(transform.offset, np.ndarray) else np.zeros(3)
                target_offset = point - motion.state.position
                
                def concentration_func(t):
                    elapsed = t - start_time
                    if elapsed >= duration:
                        return target_offset
                    factor = elapsed / duration
                    # Ease in-out
                    factor = 0.5 * (1 - np.cos(np.pi * factor))
                    return initial_offset + (target_offset - initial_offset) * factor
                    
                transform.offset = concentration_func
                transform.enabled = True

    def apply_dispersion(self, macro_id: str, force: float = 2.0, duration: float = 1.5):
        """Aplicar dispersión desde el centro"""
        if macro_id not in self._macros:
            return
            
        macro = self._macros[macro_id]
        
        # Calcular centro actual
        positions = []
        for sid in macro.source_ids:
            if sid in self._positions:
                positions.append(self._positions[sid])
                
        if not positions:
            return
            
        center = np.mean(positions, axis=0)
        
        # Aplicar fuerza de dispersión
        start_time = self._time
        for sid in macro.source_ids:
            if sid not in self._source_motions:
                continue
                
            motion = self._source_motions[sid]
            transform = motion.components.get('trajectory_transform')
            
            if isinstance(transform, TrajectoryTransform):
                # Dirección de dispersión
                direction = motion.state.position - center
                if np.linalg.norm(direction) > 0.001:
                    direction = direction / np.linalg.norm(direction)
                else:
                    # Dirección aleatoria si está en el centro
                    angle = np.random.uniform(0, 2 * np.pi)
                    direction = np.array([np.cos(angle), np.sin(angle), 0])
                    
                initial_offset = transform.offset.copy() if isinstance(transform.offset, np.ndarray) else np.zeros(3)
                target_offset = direction * force
                
                def dispersion_func(t):
                    elapsed = t - start_time
                    if elapsed >= duration:
                        return target_offset
                    factor = elapsed / duration
                    # Ease out
                    factor = 1.0 - (1.0 - factor) ** 2
                    return initial_offset + (target_offset - initial_offset) * factor
                    
                transform.offset = dispersion_func
                transform.enabled = True

    def apply_orientation_preset(self, macro_id: str, preset_name: str,
                                       intensity: float = 1.0, 
                                       time_offset_spread: float = 0.0):
        """
        Aplicar un preset de orientación a todas las fuentes de un macro
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        preset_name : str
            Nombre del preset a aplicar
        intensity : float, optional
            Intensidad de la modulación (0.0-1.0), por defecto 1.0
        time_offset_spread : float, optional
            Desfase temporal entre fuentes en segundos, por defecto 0.0
            
        Returns
        -------
        bool
            True si se aplicó correctamente, False en caso de error
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no encontrado")
            return False
            
        macro = self._macros[macro_id]
        
        for sid in macro.source_ids:
            if sid in self.orientation_modulators:
                modulator = self.orientation_modulators[sid]
                modulator.apply_preset(preset_name)
                logger.debug(f"Preset '{preset_name}' aplicado a fuente {sid}")
                
        logger.info(f"Preset de orientación '{preset_name}' aplicado a macro {macro_id}")

        return True

    def set_modulator_intensity(self, intensity: float, macro_id: Optional[str] = None):
        """Establecer intensidad del modulador (0-1)"""
        intensity = np.clip(intensity, 0.0, 1.0)
        
        if macro_id:
            # Aplicar solo a un macro
            if macro_id in self._macros:
                macro = self._macros[macro_id]
                for sid in macro.source_ids:
                    if sid in self.orientation_modulators:
                        self.orientation_modulators[sid].intensity = intensity
        else:
            # Aplicar globalmente
            self.global_modulator_intensity = intensity
            for modulator in self.orientation_modulators.values():
                modulator.intensity = intensity
                
        logger.info(f"Intensidad del modulador establecida a {intensity:.1%}")

    def update(self, dt: float) -> Dict[str, Any]:
        # Aplicar rotaciones de trayectorias
        self._apply_trajectory_rotations()

        """
        # 🔧 CORRECCIÓN FINAL: Verificar si está pausado ANTES de cualquier procesamiento
        if hasattr(self, "time_paused") and self.time_paused:
            return {"positions": {}, "orientations": {}, "apertures": {}, "names": {}, "time": self.time + dt, "frame": getattr(self, "_frame_count", 0) + 1}
        
        # También verificar usando is_paused() si existe
        if hasattr(self, "is_paused") and self.is_paused():
            return {"positions": {}, "orientations": {}, "apertures": {}, "names": {}, "time": self.time + dt, "frame": getattr(self, "_frame_count", 0) + 1}

        # 🔧 CORRECCIÓN: Verificar si está pausado
        if self.is_paused():
            return {}

        Actualizar el sistema completo - VERSIÓN OPTIMIZADA
        Solo procesa fuentes que están en macros activos
        """
        t = self._time
        
        # ========== DETERMINAR FUENTES ACTIVAS ==========
        active_sources = set()
        for macro in self._macros.values():
            active_sources.update(macro.source_ids)
        
        # Si no hay fuentes activas, no hacer nada
        if not active_sources:
            self._time += dt
            self._frame_count += 1
            return {
                'positions': {},
                'orientations': {},
                'apertures': {},
                'names': {},
                'time': self._time,
                'frame': self._frame_count
            }
        
        # ========== ACTUALIZAR SOLO FUENTES ACTIVAS ==========
        for sid in active_sources:
            if sid not in self._source_motions:
                continue
                
            motion = self._source_motions[sid]
            # 🔧 CORRECCIÓN FINAL: Verificar si componentes individuales están habilitados
            # Esto respeta el sistema de pausa del TEST 7 que deshabilita componentes
            individual_traj = motion.components.get("individual_trajectory")
            if individual_traj and hasattr(individual_traj, "enabled") and not individual_traj.enabled:
                # Saltar esta fuente si el componente individual está deshabilitado
                continue

            # CORRECCIÓN DEFINITIVA: Llamada motion.update() y manejo del retorno
            result = motion.update(t, dt)
            if isinstance(result, tuple) and len(result) == 3:
                # motion.update() retornó tupla (pos, orient, aperture)
                pos, orient, aperture = result
            else:
                # motion.update() retornó MotionState, extraer valores
                state = result if hasattr(result, 'position') else motion.state
                pos = state.position
                orient = state.orientation
                aperture = state.aperture
            
            
            # Actualizar arrays globales
            self._positions[sid] = pos
            self._orientations[sid] = orient
            self._apertures[sid] = aperture
        
        
        # ========== ACTUALIZAR TRAYECTORIAS DE MACRO ==========
        for macro_id, macro in self._macros.items():
            if hasattr(macro, 'trajectory_component') and macro.trajectory_component and macro.trajectory_component.enabled:
                # Actualizar la trayectoria del macro
                # Obtener estado del macro para actualización
                if macro.source_ids:
                    positions = [self._positions[sid] for sid in macro.source_ids if sid in active_sources]
                    if positions:
                        import numpy as np
                        from trajectory_hub.core.motion_components import MotionState
                        
                        # Centro actual del macro
                        center_pos = np.mean(positions, axis=0)
                        
                        # Estado para el macro
                        macro_state = MotionState()
                        macro_state.position = center_pos.copy()
                        
                        # Actualizar (retorna nuevo estado)
                        new_state = macro.trajectory_component.update(macro_state, t, dt)
                        
                        # Calcular desplazamiento
                        macro_offset = new_state.position - center_pos
                    else:
                        macro_offset = None
                else:
                    macro_offset = None
                
                # Aplicar el desplazamiento a todas las fuentes del macro
                if macro_offset is not None:
                    for sid in macro.source_ids:
                        if sid in active_sources and sid in self._source_motions:
                            # Aplicar offset a la posición
                            self._positions[sid] = self._positions[sid] + macro_offset
        
        # ========== ACTUALIZAR MODULADORES (solo activos) ==========
        if self.enable_modulator:
            current_time = time.time()
            for sid in active_sources:
                if sid in self.orientation_modulators:
                    modulator = self.orientation_modulators[sid]
                    if modulator.enabled:
                        # Actualizar estado con modulación
                        motion = self._source_motions[sid]
                        motion.state = modulator.update(motion.state, current_time, dt)                        # Actualizar arrays globales con las nuevas orientaciones
                        self._orientations[sid] = motion.state.orientation
                        self._apertures[sid] = motion.state.aperture
        
        # ========== ENVIAR ACTUALIZACIONES OSC (solo activos) ==========
        if self.osc_bridge and self._check_rate_limit():
            for sid in active_sources:
                # Enviar posición siempre
                self.osc_bridge.send_position(sid, self._positions[sid])
                
                # Enviar orientación y apertura si el modulador está activo
                if self.enable_modulator and sid in self.orientation_modulators:
                    modulator = self.orientation_modulators[sid]
                    if modulator.enabled:
                        # Verificar cambios en orientación
                        orientation_changed = False
                        if sid not in self._last_orientations:
                            orientation_changed = True
                        else:
                            orientation_diff = np.linalg.norm(
                                self._orientations[sid] - self._last_orientations[sid]
                            )
                            if orientation_diff > self._orientation_update_threshold:
                                orientation_changed = True
                        
                        # Verificar cambios en apertura
                        aperture_changed = False
                        if sid not in self._last_apertures:
                            aperture_changed = True
                        else:
                            aperture_diff = abs(self._apertures[sid] - self._last_apertures[sid])
                            if aperture_diff > self._aperture_update_threshold:
                                aperture_changed = True
                        
                        # Enviar orientación si cambió
                        if orientation_changed:
                            self.osc_bridge.send_orientation(
                                sid,
                                self._orientations[sid][0],  # yaw
                                self._orientations[sid][1],  # pitch
                                self._orientations[sid][2]   # roll
                            )
                            self._last_orientations[sid] = self._orientations[sid].copy()
                        
                        # Enviar apertura si cambió (independientemente de la orientación)
                        if aperture_changed:
                            self.osc_bridge.send_aperture(sid, self._apertures[sid])
                            self._last_apertures[sid] = self._apertures[sid]
        
        # Incrementar tiempo
        self._time += dt
        self._frame_count += 1
        
        # Preparar respuesta solo con fuentes activas
        active_positions = {sid: self._positions[sid] for sid in active_sources}
        active_orientations = {sid: self._orientations[sid] for sid in active_sources}
        active_apertures = {sid: self._apertures[sid] for sid in active_sources}
        active_names = {sid: self._source_info[sid].name for sid in active_sources if sid in self._source_info}
        
        # Preparar datos para OSC
        osc_data = self._prepare_osc_data()
        
        return {
            'positions': osc_data['positions'],
            'orientations': osc_data['orientations'],
            'apertures': osc_data['apertures'],
            'names': osc_data['names'],
            'time': self._time,
            'frame': self._frame_count
        }

    
    def _prepare_osc_data(self):
        """Preparar datos para envío OSC en formato correcto"""
        active_sources = set()
        for macro in self._macros.values():
            active_sources.update(macro.source_ids)
        
        # Convertir a arrays numpy para OSC
        positions_list = []
        orientations_list = []
        apertures_list = []
        names_dict = {}
        
        for sid in sorted(active_sources):
            if sid in self._source_motions:
                # Posición
                pos = self._positions[sid]
                positions_list.append(pos.tolist() if hasattr(pos, 'tolist') else list(pos))
                
                # Orientación
                orient = self._orientations[sid]
                orientations_list.append(orient.tolist() if hasattr(orient, 'tolist') else list(orient))
                
                # Apertura
                apertures_list.append(float(self._apertures[sid]))
                
                # Nombre
                if sid in self._source_info:
                    names_dict[sid] = str(self._source_info[sid].name)
        
        return {
            'positions': positions_list,
            'orientations': orientations_list,
            'apertures': apertures_list,
            'names': names_dict,
            'count': len(positions_list)
        }

    def step(self, dt: float = None) -> dict:
        """
        Step simple que aplica concentración directamente.
        """
        if dt is None:
            dt = self.dt
        
        # Para cada macro con concentración
        for macro_id, macro in self._macros.items():
            factor = getattr(macro, 'concentration_factor', 0)
            if factor > 0 and hasattr(macro, 'source_ids'):
                # Obtener posiciones actuales
                positions = []
                source_list = list(macro.source_ids)
                
                for sid in source_list:
                    if sid < self.max_sources:
                        # Usar la posición del motion si existe
                        if sid in self._source_motions:
                            pos = self._source_motions[sid].state.position.copy()
                        else:
                            pos = self._positions[sid].copy()
                        positions.append(pos)
                
                if len(positions) > 1:
                    # Calcular centro
                    import numpy as np
                    center = np.mean(positions, axis=0)
                    
                    # Mover cada fuente hacia el centro
                    for i, sid in enumerate(source_list):
                        if sid < self.max_sources:
                            # Calcular nueva posición
                            current_pos = positions[i]
                            direction = center - current_pos
                            new_pos = current_pos + (direction * factor * dt * 10.0)  # *10 para velocidad visible
                            
                            # Actualizar
                            self._positions[sid] = new_pos
                            
                            # También actualizar el motion si existe
                            if sid in self._source_motions:
                                self._source_motions[sid].state.position = new_pos.copy()
        
        # Para fuentes sin macro, mantener sincronizado
        for sid in self._source_motions:
            if sid < self.max_sources:
                motion = self._source_motions[sid]
                # Si el motion no se actualizó arriba, usar su posición
                in_macro = any(sid in macro.source_ids for macro in self._macros.values() 
                              if hasattr(macro, 'source_ids'))
                if not in_macro:
                    self._positions[sid] = motion.state.position.copy()
                
                # Actualizar orientación y apertura
                self._orientations[sid] = motion.state.orientation
                self._apertures[sid] = motion.state.aperture
        
        # Incrementar tiempo
        self._time = getattr(self, '_time', 0.0) + dt
        self._frame_count = getattr(self, '_frame_count', 0) + 1
        
        
        # Enviar posiciones via OSC si está activo
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            try:
                # Preparar datos para enviar
                active_sources = []
                active_positions = []
                active_orientations = []
                
                for sid in range(self.max_sources):
                    if sid in self._source_motions:
                        active_sources.append(sid)
                        active_positions.append(self._positions[sid])
                        active_orientations.append(self._orientations[sid])
                
                if active_sources:
                    # Enviar batch de posiciones
                    import numpy as np
                    positions_array = np.array(active_positions)
                    orientations_array = np.array(active_orientations)
                    
                    self.osc_bridge.send_batch_positions(
                        active_sources,
                        positions_array,
                        orientations_array
                    )
            except Exception as e:
                # No fallar si hay error OSC
                pass
        
        return {
            'positions': self._positions.copy(),
            'orientations': self._orientations.copy(),
            'apertures': self._apertures.copy(),
            'time': self._time,
            'frame': self._frame_count
        }
    def is_paused(self) -> bool:
        """Verificar si el sistema está globalmente pausado"""
        return getattr(self, 'time_paused', False)

    def __del__(self):
        """Limpieza al destruir"""

    # ========================================
    # MÉTODOS DE PAUSA/REANUDACIÓN DE MACROS
    # ========================================
    
    def pause_macro(self, macro_id: str) -> bool:
        """
        Pausa un macro específico deshabilitando todos sus componentes de movimiento.
        
        CORRECCIÓN CRÍTICA: GUARDAR estados ANTES de deshabilitar componentes
        
        Parameters
        ----------
        macro_id : str
            ID del macro a pausar
            
        Returns
        -------
        bool
            True si se pausó correctamente, False en caso contrario
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no encontrado")
            return False
            
        macro = self._macros[macro_id]
        
        # Verificar si ya está pausado
        if hasattr(macro, '_pause_state') and macro._pause_state.get('is_paused', False):
            logger.warning(f"Macro {macro_id} ya está pausado")
            return True
            
        # Inicializar estructura separada
        if not hasattr(macro, '_pause_state'):
            macro._pause_state = {
                'is_paused': False,
                'macro_states': {},
                'source_states': {}
            }
        
        macro._pause_state['is_paused'] = True
        macro._pause_state['macro_states'].clear()
        macro._pause_state['source_states'].clear()
        
        # 🔧 ORDEN CORRECTO: Primero GUARDAR estado del macro (ANTES de deshabilitar)
        if hasattr(macro, 'trajectory_component') and macro.trajectory_component:
            if hasattr(macro.trajectory_component, 'enabled'):
                # ✅ GUARDAR ANTES de deshabilitar
                macro._pause_state['macro_states']['trajectory_enabled'] = macro.trajectory_component.enabled
                logger.debug(f"Guardado trajectory_component.enabled = {macro.trajectory_component.enabled}")
        
        # 🔧 ORDEN CORRECTO: GUARDAR estados de fuentes ANTES de deshabilitar
        paused_count = 0
        for source_id in macro.source_ids:
            if source_id in self._source_motions:
                motion = self._source_motions[source_id]
                saved_state = {}
                
                # ✅ GUARDAR estados de trayectoria individual ANTES de cambiar
                if 'individual_trajectory' in motion.components:
                    traj = motion.components['individual_trajectory']
                    saved_state['traj_mode'] = getattr(traj, 'movement_mode', None)
                    saved_state['traj_enabled'] = getattr(traj, 'enabled', True)  # ✅ VALOR ORIGINAL
                    saved_state['traj_position'] = getattr(traj, 'position_on_trajectory', 0.0)
                    saved_state['traj_speed'] = getattr(traj, 'movement_speed', 1.0)
                    logger.debug(f"Guardado traj_enabled = {saved_state['traj_enabled']} ANTES de cambiar")
                
                # ✅ GUARDAR estados de TODOS los componentes ANTES de deshabilitar
                for comp_name, component in motion.components.items():
                    if hasattr(component, 'enabled'):
                        # ✅ GUARDAR VALOR ORIGINAL (antes de deshabilitar)
                        original_enabled = component.enabled
                        saved_state[f'motion_{comp_name}_enabled'] = original_enabled
                        logger.debug(f"Guardado {comp_name}.enabled = {original_enabled} ANTES de deshabilitar")
                
                # ✅ GUARDAR PRIMERO en source_states
                macro._pause_state['source_states'][source_id] = saved_state
                logger.debug(f"Estados de fuente {source_id} guardados ANTES de deshabilitar")
                
                paused_count += 1
        
        # 🔧 AHORA SÍ: DESHABILITAR después de guardar
        logger.debug("AHORA deshabilitando componentes DESPUÉS de guardar estados...")
        
        # Deshabilitar trajectory_component del macro
        if hasattr(macro, 'trajectory_component') and macro.trajectory_component:
            if hasattr(macro.trajectory_component, 'enabled'):
                macro.trajectory_component.enabled = False
                logger.debug("Deshabilitado trajectory_component DESPUÉS de guardar")
        
        # Deshabilitar componentes de fuentes
        for source_id in macro.source_ids:
            if source_id in self._source_motions:
                motion = self._source_motions[source_id]
                
                # Cambiar trayectoria individual a FREEZE
                if 'individual_trajectory' in motion.components:
                    traj = motion.components['individual_trajectory']
                    try:
                        from trajectory_hub.core.motion_components import TrajectoryMovementMode
                        if hasattr(traj, 'set_movement_mode'):
                            traj.set_movement_mode(TrajectoryMovementMode.FREEZE)
                        if hasattr(traj, 'enabled'):
                            traj.enabled = False
                        logger.debug(f"Deshabilitado individual_trajectory en fuente {source_id}")
                    except ImportError:
                        logger.warning("No se pudo importar TrajectoryMovementMode")
                
                # Deshabilitar TODOS los otros componentes
                for comp_name, component in motion.components.items():
                    if hasattr(component, 'enabled'):
                        component.enabled = False
                        logger.debug(f"Deshabilitado {comp_name} en fuente {source_id}")
        
        logger.info(f"Macro {macro_id} pausado - {paused_count} fuentes, ORDEN CORRECTO aplicado")
        return True
    def resume_macro(self, macro_id: str) -> bool:
        """
        Reanuda un macro pausado restaurando el estado de todas sus fuentes.
        
        CORRECCIÓN DEFINITIVA: Lee estructura _pause_state correctamente separada
        
        Parameters
        ----------
        macro_id : str
            ID del macro a reanudar
            
        Returns
        -------
        bool
            True si se reanudó correctamente, False en caso contrario
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no encontrado")
            return False
            
        macro = self._macros[macro_id]
        
        if not hasattr(macro, '_pause_state') or not macro._pause_state.get('is_paused', False):
            logger.warning(f"Macro {macro_id} no está pausado")
            return True
            
        # 🔧 RESTAURAR ESTADO DEL MACRO (separado)
        if 'macro_states' in macro._pause_state:
            macro_states = macro._pause_state['macro_states']
            
            if hasattr(macro, 'trajectory_component') and macro.trajectory_component:
                if 'trajectory_enabled' in macro_states:
                    macro.trajectory_component.enabled = macro_states['trajectory_enabled']
                    logger.debug(f"Restaurado trajectory_component.enabled = {macro.trajectory_component.enabled}")
        
        # 🔧 RESTAURAR ESTADOS DE LAS FUENTES (separado)
        resumed_count = 0
        if 'source_states' in macro._pause_state:
            source_states = macro._pause_state['source_states']
            
            for source_id, saved_state in source_states.items():
                if isinstance(source_id, int) and source_id in self._source_motions:
                    motion = self._source_motions[source_id]
                    logger.debug(f"Restaurando fuente {source_id}")
                    
                    # Restaurar trayectoria individual
                    if 'individual_trajectory' in motion.components:
                        traj = motion.components['individual_trajectory']
                        
                        if 'traj_mode' in saved_state and hasattr(traj, 'set_movement_mode'):
                            try:
                                traj.set_movement_mode(
                                    saved_state['traj_mode'],
                                    movement_speed=saved_state.get('traj_speed', 1.0)
                                )
                                logger.debug(f"Restaurado modo de trayectoria: {saved_state['traj_mode']}")
                            except Exception as e:
                                logger.warning(f"Error restaurando modo de trayectoria: {e}")
                        
                        if 'traj_position' in saved_state and hasattr(traj, 'position_on_trajectory'):
                            traj.position_on_trajectory = saved_state['traj_position']
                            logger.debug(f"Restaurado position_on_trajectory: {saved_state['traj_position']}")
                        
                        if 'traj_enabled' in saved_state and hasattr(traj, 'enabled'):
                            traj.enabled = saved_state['traj_enabled']
                            logger.debug(f"Restaurado individual_trajectory.enabled = {traj.enabled}")
                    
                    # 🔧 RESTAURAR OTROS COMPONENTES con claves correctas
                    for comp_name, component in motion.components.items():
                        enabled_key = f'motion_{comp_name}_enabled'
                        if enabled_key in saved_state and hasattr(component, 'enabled'):
                            component.enabled = saved_state[enabled_key]
                            logger.debug(f"Restaurado {comp_name}.enabled = {component.enabled}")
                    
                    resumed_count += 1
        
        # Limpiar estado de pausa
        macro._pause_state['is_paused'] = False
        macro._pause_state['macro_states'].clear()
        macro._pause_state['source_states'].clear()
        
        logger.info(f"Macro {macro_id} reanudado - {resumed_count} fuentes, estructura corregida")
        return True
    def toggle_macro_pause(self, macro_id: str) -> bool:
        """
        Alterna entre pausado y activo para un macro específico.
        
        Parameters
        ----------
        macro_id : str
            ID del macro
            
        Returns
        -------
        bool
            True si ahora está pausado, False si está activo
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no encontrado")
            return False
            
        macro = self._macros[macro_id]
        
        # Verificar estado actual
        is_paused = hasattr(macro, '_pause_state') and macro._pause_state.get('is_paused', False)
        
        if is_paused:
            self.resume_macro(macro_id)
            return False
        else:
            self.pause_macro(macro_id)
            return True
    
    def pause_all_macros(self) -> int:
        """
        Pausa todos los macros activos en el sistema.
        
        Returns
        -------
        int
            Número de macros pausados
        """
        paused_count = 0
        
        for macro_id in list(self._macros.keys()):
            if self.pause_macro(macro_id):
                paused_count += 1
                
        logger.info(f"Pausados {paused_count} macros en total")
        return paused_count
    
    def resume_all_macros(self) -> int:
        """
        Reanuda todos los macros pausados en el sistema.
        
        Returns
        -------
        int
            Número de macros reanudados
        """
        resumed_count = 0
        
        for macro_id in list(self._macros.keys()):
            macro = self._macros[macro_id]
            if hasattr(macro, '_pause_state') and macro._pause_state.get('is_paused', False):
                if self.resume_macro(macro_id):
                    resumed_count += 1
                    
        logger.info(f"Reanudados {resumed_count} macros en total")
        return resumed_count
    
    def _apply_trajectory_rotations(self):
        """Aplicar rotaciones a las trayectorias individuales"""
        if not hasattr(self, 'trajectory_rotations'):
            return
            
        for source_id, rotation_data in self.trajectory_rotations.items():
            if source_id not in self._source_motions:
                continue
                
            motion = self._source_motions[source_id]
            traj = motion.components.get('individual_trajectory')
            
            if traj and hasattr(traj, 'center'):
                # Obtener posición actual
                current_pos = motion.state.position
                
                # Aplicar rotación alrededor del centro de la trayectoria
                rel_pos = current_pos - traj.center
                rotation_matrix = rotation_data['matrix']
                rotated_pos = rotation_matrix @ rel_pos
                
                # Nueva posición
                motion.state.position = traj.center + rotated_pos

    def get_macro_pause_state(self, macro_id: str) -> Optional[Dict]:
        """
        Obtiene el estado de pausa de un macro.
        
        Parameters
        ----------
        macro_id : str
            ID del macro
            
        Returns
        -------
        Optional[Dict]
            Diccionario con información del estado de pausa o None si el macro no existe
        """
        if macro_id not in self._macros:
            return None
            
        macro = self._macros[macro_id]
        
        if not hasattr(macro, '_pause_state'):
            return {'is_paused': False, 'pause_time': None}
            
        return {
            'is_paused': macro._pause_state.get('is_paused', False),
            'pause_time': macro._pause_state.get('pause_time', None),
            'paused_sources': len(macro._pause_state.get('saved_states', {}))
        }
        self.stop()        
    def _calculate_rotation_matrix(self, pitch, yaw, roll):
        """Calcular matriz de rotación 3x3"""
        import numpy as np
        cx, sx = np.cos(pitch), np.sin(pitch)
        cy, sy = np.cos(yaw), np.sin(yaw)
        cz, sz = np.cos(roll), np.sin(roll)
        rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
        return rz @ ry @ rx

