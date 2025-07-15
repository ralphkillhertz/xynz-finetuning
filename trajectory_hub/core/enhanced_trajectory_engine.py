"""
enhanced_trajectory_engine.py - Motor de trayectorias con sistema de componentes completo
Evolución de extended_path_engine.py que mantiene compatibilidad e integra motion_components
"""
from __future__ import annotations
import math
import numpy as np


try:
    # from rotation_system import ... # Archivo no existe
    pass
except ImportError:
    print('⚠️ rotation_system.py no encontrado')
    MacroRotation = None
import logging
import time
import threading
from typing import List, Dict, Optional, Callable, Set, Tuple, Any, Union
from dataclasses import dataclass, field

# Importar el sistema de componentes
from trajectory_hub.core.motion_components import (
    MacroRotation,
    MotionDelta,
    SourceMotion,
    TrajectoryMovementMode,
    TrajectoryDisplacementMode,
    OrientationModulation,
    IndividualTrajectory,
    TrajectoryTransform,
    MacroTrajectory,
    MotionState,
    AdvancedOrientationModulation,
    ConcentrationComponent,
    ConcentrationMode,
    ConcentrationCurve,
    MacroRotation
)
from trajectory_hub.core.trajectory_deformers import (
    CompositeDeformer, ForceFieldDeformation, WaveDeformation,
    ChaoticDeformation, GestureDeformation, BlendMode
)
from trajectory_hub.core.playback_modes import (
    PlaybackMode, PlaybackController, TrajectoryPlaybackManager
)
# Mantener compatibilidad con el sistema anterior
from trajectory_hub.core.extended_path_engine import (
    BoidParams, SourceInfo, MacroSource,
    _NUMBA_AVAILABLE, _BEHAVIORS_AVAILABLE
)
# from trajectory_hub.core.rotation_system import ... # Archivo no existe

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
            
            # IMPORTANTE: No aplicar formación circular por defecto
            # Esto será establecido por create_macro
            self.formation_type = None
            
        except Exception as e:
            # Si hay algún problema, inicializar manualmente los atributos críticos
            logger.warning(f"Error en __post_init__: {e}. Inicializando manualmente.")
            if not hasattr(self, 'source_ids'):
                self.source_ids = []  # Lista, no set
            if not hasattr(self, 'behavior'):
                self.behavior = None
                
        # Asegurar que trajectory_component se inicialice
        if self.trajectory_component is None:
            from trajectory_hub.core.motion_components import MotionDelta, MacroTrajectory
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
        self.running = False
        self._update_thread = None
        self._next_source_id = 0  # Contador global para IDs únicos (comienza en 0)
        self.fps = fps
        
        # Sistema OSC
        from .spat_osc_bridge import SpatOSCBridge
        
        self.osc_bridge = SpatOSCBridge()
        logger.info(f"OSC bridge inicializado: {self.osc_bridge is not None}")
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
        self._is_running = False  # IMPORTANTE: No iniciar el loop automáticamente

        logger.info(f"EnhancedTrajectoryEngine inicializado ({max_sources} fuentes @ {fps} fps)")

        # Diccionarios para tracking de cambios
        self._last_positions = {}
        self._last_orientations = {}
        self._last_apertures = {}
        self.time_paused = False
        # Sistema de rotación
        self.macro_rotations = {}
        self.trajectory_rotations = {}
        
        # Sistema de playback modes
        self.playback_manager = TrajectoryPlaybackManager()


   
        # Sistema de rotación algorítmica
        self.macro_rotations_algo = {}  # MacroRotation objects
        self.trajectory_rotations_algo = {}  # TrajectoryRotation objects
        self._rotation_time = 0.0  # Tiempo para las rotaciones algorítmicas
 
        self._macros = {}  # Almacén de macros
        self.motion_states = {}  # Dict[int, SourceMotion]

        # Conjunto de fuentes activas
        self._active_sources = set()

    def start(self):
        """Inicia el loop de actualización"""
        if not self.running:
            self.running = True
            self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self._update_thread.start()
            print("✅ Engine iniciado - Loop activo")
    
    def stop(self):
        """Detiene el loop de actualización"""
        if self.running:
            self.running = False
            if self._update_thread:
                self._update_thread.join(timeout=1.0)
            print("🛑 Engine detenido")
    
    def _update_loop(self):
        """Loop principal que llama a update() continuamente"""
        # Usar 60 fps directamente ya que self.config no existe
        update_rate = 60
        dt = 1.0 / update_rate
        
        while self.running:
            try:
                self.update(dt)
                time.sleep(dt)
            except Exception as e:
                print(f"Error en update loop: {e}")
                # No imprimir traceback completo para no ensuciar output
                pass
    

    def create_source(self, source_id: int, name: str = None):
        """Crea una nueva fuente de sonido"""
        if source_id >= self.max_sources:
            raise ValueError(f"ID {source_id} excede el máximo de fuentes ({self.max_sources})")
        
        if source_id in self.motion_states:
            print(f"⚠️ Fuente {source_id} ya existe")
            return self.motion_states[source_id]
        
        # Crear estado inicial
        state = MotionState()
        state.source_id = source_id
        state.position = self._positions[source_id].copy()
        state.velocity = np.zeros(3)
        state.name = name or f"source_{source_id}"
        
        # Crear SourceMotion básico
        motion = SourceMotion(state)
        motion.source_id = source_id
        
        # Registrar
        self.motion_states[source_id] = motion
        self._source_motions[source_id] = motion
        self._active_sources.add(source_id)
        
        # Notificar al bridge OSC si existe
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            try:
                self.osc_bridge.source_created(source_id, state.name)
                # Mutear la fuente por defecto
                spat_id = source_id + 1  # Convertir a ID de SPAT
                self.osc_bridge.mute_source(spat_id, True)
            except:
                pass
        
        print(f"✅ Fuente {source_id} creada: {state.name}")
        return motion
        
    def create_orientation_modulator(self, source_id: int) -> Optional[AdvancedOrientationModulation]:
        """Crear modulador de orientación para una fuente"""
        if not self.enable_modulator:
            return None
            
        if source_id not in self.motion_states:
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
                # Generar ID único
                sid = self._next_source_id
                self._next_source_id += 1
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
        
        # Guardar información de formación en el macro
        macro.formation = formation
        macro.spacing = spacing
        # IMPORTANTE: También actualizar formation_type para evitar que se use el default "circle"
        macro.formation_type = formation
        macro.formation_spacing = spacing
        
        # Si hay función personalizada, guardarla temporalmente y en el macro
        if 'custom_function' in kwargs and kwargs['custom_function']:
            self._custom_formation_function = kwargs['custom_function']
            macro.custom_function = kwargs['custom_function']
        
        # Aplicar formación inicial ANTES de registrar el macro (como en los backups que funcionaban)
        self._apply_formation(source_ids, formation, spacing)
        
        # Limpiar función personalizada después de usarla
        if hasattr(self, '_custom_formation_function'):
            delattr(self, '_custom_formation_function')
        
        # Registrar macro DESPUÉS de aplicar la formación
        self._macros[macro_id] = macro

        # IMPORTANTE: Añadir trajectory_component a cada fuente
        if hasattr(macro, "trajectory_component") and macro.trajectory_component:
            for sid in macro.source_ids:
                if sid in self.motion_states:
                    self.motion_states[sid].active_components["macro_trajectory"] = macro.trajectory_component
                    logger.debug(f"macro_trajectory añadido a fuente {sid}")

        
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
            

        # Enviar configuración a SPAT inmediatamente
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            try:
                # 1. Nombrar las fuentes según el formato Macro_name_n
                # Convertir source_ids a IDs de SPAT (sumando 1)
                spat_source_ids = [sid + 1 for sid in source_ids]
                self.osc_bridge.set_macro_source_names(name, spat_source_ids)
                
                # 2. Seleccionar las fuentes en SPAT (para agruparlas visualmente)
                self.osc_bridge.select_sources(spat_source_ids, True)
                
                # 3. Obtener posiciones del macro recién creado
                macro = self._macros[macro_id]
                positions = {}
                
                # Obtener posiciones directamente del array _positions
                for source_id in macro.source_ids:
                    if source_id < len(self._positions):
                        pos = self._positions[source_id]
                        # Usar source_id como clave (0-based para trajectory_hub)
                        positions[source_id] = (float(pos[0]), float(pos[1]), float(pos[2]))
                
                # Enviar si hay posiciones
                if positions:
                    self.osc_bridge.send_source_positions(positions)
                    print(f"📡 Enviadas {len(positions)} posiciones a Spat")
                    
                # 4. Desmutear las fuentes del macro (estado por defecto es mute)
                for spat_id in spat_source_ids:
                    self.osc_bridge.mute_source(spat_id, False)
                print(f"   🔊 {len(spat_source_ids)} fuentes desmuteadas")
                
                # 5. Deseleccionar las fuentes después de configurar
                self.osc_bridge.select_sources(spat_source_ids, False)
                
            except Exception as e:
                print(f"Error enviando OSC: {e}")
        
        
        return macro_id


    def list_macros(self):
        """Lista todos los macros activos con información detallada
        
        Returns:
            list: Lista de diccionarios con info de cada macro
        """
        macro_list = []
        
        for macro_key, macro in self._macros.items():
            # Extraer nombre limpio del macro
            # Formato esperado: macro_N_nombre
            parts = macro_key.split('_', 2)
            macro_name = parts[2] if len(parts) > 2 else macro_key
            
            # Obtener formación guardada o intentar determinarla del nombre
            formation = getattr(macro, 'formation', None)
            if not formation:
                formation = "unknown"
                formations = ["circle", "line", "grid", "spiral", "random", "sphere", "custom"]
                for form in formations:
                    if form in macro_name.lower():
                        formation = form
                        break
            
            # Recopilar información del macro
            macro_info = {
                'key': macro_key,  # ID completo
                'name': macro_name,  # Nombre limpio
                'num_sources': len(macro.source_ids) if hasattr(macro, 'source_ids') else 0,
                'source_ids': list(macro.source_ids) if hasattr(macro, 'source_ids') else [],
                'behavior': macro.behavior_name if hasattr(macro, 'behavior_name') else 'unknown',
                'formation': formation,
                'spacing': getattr(macro, 'spacing', 2.0)
            }
            macro_list.append(macro_info)
        
        return macro_list


    def select_macro(self, identifier):
        """Selecciona un macro por nombre o ID
        
        Args:
            identifier: Puede ser:
                - ID completo (macro_0_nombre)
                - Nombre parcial (nombre)
                - Índice del macro (0, 1, 2...)
            
        Returns:
            dict: Información del macro o None si no se encuentra
        """
        if not self._macros:
            return None
        
        # Buscar por ID exacto
        if identifier in self._macros:
            macro = self._macros[identifier]
            # Extraer nombre del identifier (formato: macro_N_nombre)
            parts = identifier.split('_', 2)
            name = parts[2] if len(parts) > 2 else identifier
            
            return {
                'key': identifier,
                'macro': macro,
                'name': name,
                'source_ids': list(macro.source_ids) if hasattr(macro, 'source_ids') else [],
                'num_sources': len(macro.source_ids) if hasattr(macro, 'source_ids') else 0,
                'behavior': macro.behavior_name if hasattr(macro, 'behavior_name') else 'unknown',
                'formation': getattr(macro, 'formation', 'circle'),
                'spacing': getattr(macro, 'spacing', 2.0)
            }
        
        # Buscar por índice si es número
        if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
            idx = int(identifier)
            macro_keys = list(self._macros.keys())
            if 0 <= idx < len(macro_keys):
                key = macro_keys[idx]
                return self.select_macro(key)  # Recursión para reusar lógica
        
        # Buscar por nombre parcial (case insensitive)
        identifier_lower = str(identifier).lower()
        
        # Primero buscar coincidencia exacta en el nombre
        for macro_id, macro in self._macros.items():
            # Extraer nombre del formato macro_N_nombre
            parts = macro_id.split('_', 2)
            macro_name = parts[2] if len(parts) > 2 else macro_id
            
            if macro_name.lower() == identifier_lower:
                return self.select_macro(macro_id)
        
        # Luego buscar coincidencia parcial
        for macro_id, macro in self._macros.items():
            if identifier_lower in macro_id.lower():
                return self.select_macro(macro_id)
        
        return None


    def delete_macro(self, identifier):
        """Elimina un macro y todas sus sources
        
        Args:
            identifier: Nombre del macro, ID completo o índice
            
        Returns:
            bool: True si se eliminó, False si no se encontró
        """
        # Primero buscar el macro usando select_macro
        macro_info = self.select_macro(identifier)
        
        if not macro_info:
            print(f"❌ Macro '{identifier}' no encontrado")
            return False
        
        macro_key = macro_info['key']
        macro = macro_info['macro']
        source_ids = macro_info['source_ids']
        
        print(f"🗑️ Eliminando macro '{macro_key}' con {len(source_ids)} sources...")
        
        # Primero restaurar nombres en SPAT antes de eliminar
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            # Convertir a IDs de SPAT (sumando 1)
            spat_source_ids = [sid + 1 for sid in source_ids]
            self.osc_bridge.restore_default_names(spat_source_ids)
            
            # Posicionar fuentes en posición por defecto (Az=0, El=0, Dist=2)
            # Convertir coordenadas esféricas a cartesianas
            # Azimuth=0, Elevation=0, Distance=2 => X=2, Y=0, Z=0
            default_positions = {}
            for source_id in source_ids:
                # Posición por defecto en coordenadas cartesianas
                # Distance=2 en eje X cuando Az=0 y El=0
                default_positions[source_id] = (2.0, 0.0, 0.0)
                
                # También actualizar el array interno
                if source_id < len(self._positions):
                    self._positions[source_id] = np.array([2.0, 0.0, 0.0])
            
            # Enviar posiciones por defecto a SPAT
            if default_positions:
                self.osc_bridge.send_source_positions(default_positions)
                print(f"   📍 Fuentes posicionadas en posición por defecto (Az=0, El=0, Dist=2)")
            
            # Mutear todas las fuentes del macro
            for spat_id in spat_source_ids:
                self.osc_bridge.mute_source(spat_id, True)
            print(f"   🔇 {len(spat_source_ids)} fuentes muteadas")
        
        # Eliminar todas las sources del macro de _active_sources
        removed_count = 0
        for source_id in source_ids:
            self._active_sources.discard(source_id)  # discard no lanza error si no existe
            removed_count += 1
            print(f"   ✅ Source {source_id} eliminada")
        
        # Eliminar el macro del diccionario
        if macro_key in self._macros:
            del self._macros[macro_key]
            print(f"✅ Macro '{macro_key}' eliminado completamente")
        
        # Actualizar contador de macros si existe
        if hasattr(self, 'macro_count'):
            self.macro_count = len(self._macros)
        
        # Log final
        print(f"✅ Eliminación completa: {removed_count} sources removidas")
        
        return True
    
    def enable_macro(self, identifier: str, enabled: bool = True):
        """Activa o desactiva un macro completo
        
        Args:
            identifier: Nombre del macro, ID completo o índice
            enabled: True para activar, False para desactivar
            
        Returns:
            bool: True si se aplicó correctamente
        """
        # Buscar el macro
        macro_info = self.select_macro(identifier)
        if not macro_info:
            print(f"❌ Macro '{identifier}' no encontrado")
            return False
        
        macro_key = macro_info['key']
        macro = macro_info['macro']
        source_ids = macro_info['source_ids']
        
        # Guardar estado actual si es la primera vez que se desactiva
        if not enabled and not hasattr(macro, '_saved_state'):
            macro._saved_state = {
                'positions': {},
                'motion_states': {}
            }
            # Guardar posiciones actuales
            for sid in source_ids:
                if sid < len(self._positions):
                    macro._saved_state['positions'][sid] = self._positions[sid].copy()
                # Guardar estados de movimiento si existen
                if sid in self.motion_states:
                    motion = self.motion_states[sid]
                    macro._saved_state['motion_states'][sid] = {
                        'velocity': motion.velocity.copy() if hasattr(motion, 'velocity') else None,
                        'active': getattr(motion, 'active', True)  # Default True si no existe
                    }
        
        # Si se reactiva y hay estado guardado, restaurarlo
        if enabled and hasattr(macro, '_saved_state'):
            for sid in source_ids:
                if sid in macro._saved_state['positions']:
                    self._positions[sid] = macro._saved_state['positions'][sid].copy()
                if sid in macro._saved_state['motion_states']:
                    saved_motion = macro._saved_state['motion_states'][sid]
                    if sid in self.motion_states:
                        motion = self.motion_states[sid]
                        if saved_motion['velocity'] is not None and hasattr(motion, 'velocity'):
                            motion.velocity = saved_motion['velocity'].copy()
                        if hasattr(motion, 'active'):
                            motion.active = saved_motion['active']
        
        # Marcar macro como activo/inactivo
        macro.enabled = enabled
        
        # Activar/desactivar fuentes en el engine
        if enabled:
            self._active_sources.update(source_ids)
        else:
            self._active_sources.difference_update(source_ids)
        
        # Enviar comandos OSC a SPAT
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            spat_source_ids = [sid + 1 for sid in source_ids]
            
            if not enabled:
                # Al desactivar, primero mutear las fuentes
                for spat_id in spat_source_ids:
                    self.osc_bridge.mute_source(spat_id, True)
                print(f"🔇 Fuentes muteadas antes de desactivar")
                # Luego desactivar
                self.osc_bridge.enable_macro_sources(spat_source_ids, False)
            else:
                # Al activar, primero activar las fuentes
                self.osc_bridge.enable_macro_sources(spat_source_ids, True)
                # Luego desmutear
                for spat_id in spat_source_ids:
                    self.osc_bridge.mute_source(spat_id, False)
                print(f"🔊 Fuentes activadas y desmuteadas")
        
        status = "activado" if enabled else "desactivado"
        print(f"✅ Macro '{macro_info['name']}' {status} ({len(source_ids)} fuentes)")
        
        return True
    
    def mute_macro(self, identifier: str, muted: bool = True):
        """Mutea o desmutea un macro en SPAT (solo audio, sin afectar posiciones)
        
        Args:
            identifier: Nombre del macro, ID completo o índice
            muted: True para mutear, False para desmutear
            
        Returns:
            bool: True si se aplicó correctamente
        """
        # Buscar el macro
        macro_info = self.select_macro(identifier)
        if not macro_info:
            print(f"❌ Macro '{identifier}' no encontrado")
            return False
        
        source_ids = macro_info['source_ids']
        
        # Enviar comandos OSC a SPAT para mutear/desmutear
        if hasattr(self, 'osc_bridge') and self.osc_bridge:
            spat_source_ids = [sid + 1 for sid in source_ids]
            for spat_id in spat_source_ids:
                self.osc_bridge.mute_source(spat_id, muted)
        
        status = "muteado" if muted else "desmuteado"
        print(f"🔇 Macro '{macro_info['name']}' {status} ({len(source_ids)} fuentes)")
        
        return True
    
    def is_macro_enabled(self, identifier: str) -> bool:
        """Verifica si un macro está activado
        
        Args:
            identifier: Nombre del macro, ID completo o índice
            
        Returns:
            bool: True si está activado, False si está desactivado o no existe
        """
        macro_info = self.select_macro(identifier)
        if not macro_info:
            return False
        
        macro = macro_info['macro']
        return getattr(macro, 'enabled', True)  # Por defecto consideramos que está activado

    def _apply_formation(self, source_ids: List[int], formation: str, spacing: float, center: Optional[np.ndarray] = None):
        """Aplicar formación inicial a un conjunto de fuentes
        
        Parameters
        ----------
        source_ids : List[int]
            IDs de las fuentes
        formation : str
            Tipo de formación
        spacing : float
            Espaciado entre fuentes
        center : np.ndarray, optional
            Centro de la formación. Si es None, usa (0,0,0)
        """
        total = len(source_ids)
        
        if total == 0:
            return
            
        # Centro de la formación (por defecto alrededor del listener)
        if center is None:
            center = np.array([0.0, 0.0, 0.0])
        else:
            center = np.array(center)  # Asegurar que es numpy array
        
        # Usar spacing por defecto si es None
        if spacing is None:
            spacing = 2.0  # Valor por defecto para separación
            
        # DEBUG: Verificar parámetros (comentado para evitar interferencias)
        # print(f"\n🔧 _apply_formation: formation='{formation}', spacing={spacing}, total={total}")
        
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
                

            elif formation == "random":
                # Formación aleatoria con concentración ajustable
                # El parámetro spacing controla la concentración (menor = más concentrado)
                import random
                
                # Distribución gaussiana para mayor concentración en el centro
                # Usar spacing como desviación estándar
                x = center[0] + random.gauss(0, spacing)
                y = center[1] + random.gauss(0, spacing)
                
                # Para Z, usar la mitad del spacing para mantenerlo más plano
                z = center[2] + random.gauss(0, spacing * 0.5)
                
            elif formation == "sphere":
                # Distribución uniforme de puntos en una esfera
                # Usando el método de espiral de Fibonacci para distribución uniforme
                
                # Golden angle en radianes
                golden_angle = np.pi * (3.0 - np.sqrt(5.0))
                
                # Calcular posición en la esfera
                # y va de -1 a 1
                y_normalized = 1 - (index / (total - 1)) * 2 if total > 1 else 0
                
                # Radio en el plano XZ basado en y
                radius_xz = np.sqrt(max(0, 1 - y_normalized * y_normalized))
                
                # Ángulo theta usando el golden angle para distribución uniforme
                theta = golden_angle * index
                
                # DEBUG temporal
                if index < 5:
                    print(f"   DEBUG sphere[{index}]: y_norm={y_normalized:.3f}, radius_xz={radius_xz:.3f}, theta={theta:.3f}")
                
                # Convertir a coordenadas cartesianas
                x = center[0] + spacing * radius_xz * np.cos(theta)
                z = center[2] + spacing * radius_xz * np.sin(theta)
                y = center[1] + spacing * y_normalized
                
                # DEBUG adicional
                if index < 5:
                    print(f"      -> Posición final: x={x:.3f}, y={y:.3f}, z={z:.3f}")
                
            elif formation == "custom" and hasattr(self, '_custom_formation_function'):
                # Formación personalizada basada en funciones matemáticas
                t = index / (total - 1) if total > 1 else 0.0
                
                # Evaluar las expresiones con contexto seguro
                x, y, z = self._evaluate_custom_formation(t, index, total)
                
                # Aplicar escala si se especificó spacing
                if spacing is not None:
                    x *= spacing
                    y *= spacing
                    z *= spacing
                    
                # Aplicar centro
                x += center[0]
                y += center[1]
                z += center[2]
                
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
        if formation in ["spiral", "sphere"]:
            z_values = []
            y_values = []
            print(f"\n   🔍 DEBUG: Formación {formation}")
            for idx, sid in enumerate(source_ids[:8]):  # Primeros 8 para sphere
                if sid in self._source_motions:
                    pos = self._source_motions[sid].state.position
                    z_values.append(pos[2])
                    y_values.append(pos[1])
                    print(f"   Fuente {sid}: x={pos[0]:.3f}, y={pos[1]:.3f}, z={pos[2]:.3f}")
            
            if formation == "sphere" and y_values:
                y_range = max(y_values) - min(y_values)
                z_range = max(z_values) - min(z_values)
                print(f"   📊 Rango Y: {y_range:.3f}, Rango Z: {z_range:.3f}")
                if y_range > 0.1 and z_range > 0.1:
                    print(f"   ✅ CORRECTO: Fuentes distribuidas en esfera 3D")
                else:
                    print(f"   ❌ PROBLEMA: Distribución no esférica")
            elif formation == "spiral" and z_values:
                z_range = max(z_values) - min(z_values)
                print(f"   📊 Rango Z: {z_range:.6f}")
                if z_range > 0.001:
                    print(f"   ✅ CORRECTO: Fuentes tienen diferentes alturas Z")
                else:
                    print(f"   ❌ PROBLEMA: Todas las fuentes tienen la misma altura Z")
        # ===== FIN PARCHE DE DEBUG =====
    def set_individual_trajectory(self, macro_id: str, source_id: int, 
                                     shape: str, shape_params: dict = None,
                                     movement_mode: str = "fix", speed: float = 1.0):
        """Configura la trayectoria individual de una fuente dentro de un macro"""
        # Verificar que el macro existe
        if macro_id not in self._macros:
            raise ValueError(f"Macro '{macro_id}' not found")
        
        macro = self._macros[macro_id]
        
        # Verificar que la fuente pertenece al macro
        if source_id not in macro.source_ids:
            raise ValueError(f"Source {source_id} not in macro '{macro_id}'")
        
        # Verificar que el motion_state existe
        if source_id not in self.motion_states:
            raise ValueError(f"Motion state for source {source_id} not found")
        
        motion = self.motion_states[source_id]
        
        # Crear el componente de trayectoria individual
        from .motion_components import IndividualTrajectory
        
        # Crear el componente sin parámetros (constructor vacío)
        trajectory = IndividualTrajectory()
        
        # Configurar usando los métodos/atributos disponibles
        # IMPORTANTE: Inicializar shape_params
        trajectory.shape_params = shape_params if shape_params is not None else {}
        
        trajectory.shape = shape
        trajectory.movement_mode = movement_mode
        trajectory.movement_speed = speed
        trajectory.enabled = True
        
        # Configurar parámetros de forma
        if shape_params is None:
            shape_params = {}
        
        # Aplicar parámetros según la forma
        if shape == "circle":
            trajectory.radius = shape_params.get('radius', 2.0)
        elif shape == "spiral":
            trajectory.scale = shape_params.get('scale', 1.0)
            trajectory.turns = shape_params.get('turns', 3)
        elif shape == "figure8":
            trajectory.scale = shape_params.get('scale', 1.0)
        elif shape == "lissajous":
            trajectory.freq_x = shape_params.get('freq_x', 2)
            trajectory.freq_y = shape_params.get('freq_y', 3)
            trajectory.scale = shape_params.get('scale', 1.0)
        
        # Si tiene método configure, usarlo
        if hasattr(trajectory, 'configure'):
            trajectory.configure(shape, shape_params, movement_mode)
        
        # Si tiene método set_shape, usarlo
        if hasattr(trajectory, 'set_shape'):
            trajectory.set_shape(shape, **shape_params)
        
        # Añadir a los componentes activos
        if hasattr(motion, 'active_components'):
            motion.active_components['individual_trajectory'] = trajectory
        else:
            motion.active_components = {'individual_trajectory': trajectory}
        
        print(f"✅ Trayectoria individual configurada para fuente {source_id} en macro '{macro_id}'")
        return True
    def set_macro_trajectory(
        self,
        macro_id: str,
        trajectory_func_or_type: Union[str, Callable[[float], np.ndarray]],
        orientation_func: Optional[Callable[[float], np.ndarray]] = None,
        enable_deformation: bool = True,
        **kwargs
    ):
        """Establecer trayectoria de un macro completo
        
        Args:
            macro_id: ID del macro
            trajectory_func_or_type: Función callable o string tipo (circle, spiral, etc.)
            orientation_func: Función opcional de orientación
            enable_deformation: Habilitar deformación
            **kwargs: Parámetros adicionales para crear la trayectoria (speed, radius, etc.)
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no existe")
            return
            
        macro = self._macros[macro_id]
        
        # Convertir string a función si es necesario
        if isinstance(trajectory_func_or_type, str):
            try:
                from trajectory_hub.core.trajectory_functions import create_trajectory_function
                trajectory_func = create_trajectory_function(trajectory_func_or_type, **kwargs)
            except Exception as e:
                logger.error(f"Error creando trayectoria '{trajectory_func_or_type}': {e}")
                return
        else:
            trajectory_func = trajectory_func_or_type
        
        # Configurar componente de trayectoria
        if macro.trajectory_component:
            # Extraer velocidad si está en kwargs
            speed = kwargs.get('speed', 1.0)
            macro.trajectory_component.set_trajectory(trajectory_func, orientation_func, speed=abs(speed))
            macro.trajectory_component.enabled = True
            
            # Crear controlador de playback para esta trayectoria
            playback_controller = self.playback_manager.create_controller(macro_id)
            
            # Configurar modo de playback (por defecto Fix)
            playback_mode = kwargs.get('playback_mode', PlaybackMode.FIX)
            playback_params = kwargs.get('playback_params', {})
            
            # Convertir string a PlaybackMode si es necesario
            if isinstance(playback_mode, str):
                try:
                    playback_mode = PlaybackMode(playback_mode.lower())
                except ValueError:
                    logger.warning(f"Modo de playback '{playback_mode}' no válido, usando FIX")
                    playback_mode = PlaybackMode.FIX
            
            # Si la velocidad es negativa, se maneja en el controlador
            playback_params['speed'] = speed
            playback_controller.set_mode(playback_mode, **playback_params)
            
            # Vincular el controlador al componente de trayectoria
            macro.trajectory_component.playback_controller = playback_controller
            
            # Pasar la función de trayectoria al playback controller para cálculos de longitud
            playback_controller.trajectory_func = trajectory_func
            
        # Habilitar deformación si se solicita
        macro.deformation_enabled = enable_deformation
        
        # Log el modo actual (puede ser string o PlaybackMode)
        mode_value = playback_mode.value if hasattr(playback_mode, 'value') else str(playback_mode)
        logger.info(f"Trayectoria configurada para macro '{macro_id}' con modo {mode_value}")
        
        logger.info(f"Trayectoria establecida para macro {macro_id}")

    def set_macro_playback_mode(self, macro_id: str, mode: Union[str, PlaybackMode], **kwargs):
        """
        Establece el modo de reproducción para un macro
        
        Args:
            macro_id: ID del macro
            mode: Modo de reproducción (fix, random, freeze, vibration, spin)
            **kwargs: Parámetros específicos del modo
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no existe")
            return
            
        # Convertir string a enum si es necesario
        if isinstance(mode, str):
            try:
                mode = PlaybackMode(mode.lower())
            except ValueError:
                logger.error(f"Modo de reproducción '{mode}' no válido")
                return
                
        # Configurar el modo en el controlador
        self.playback_manager.set_mode_for_trajectory(macro_id, mode, **kwargs)
        logger.info(f"Modo de reproducción '{mode.value}' establecido para macro '{macro_id}'")
    
    def freeze_macro(self, macro_id: str):
        """Congela un macro en su posición actual"""
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no existe")
            return
            
        macro = self._macros[macro_id]
        if macro.trajectory_component:
            current_position = macro.trajectory_component.phase
            self.playback_manager.freeze_trajectory(macro_id, current_position)
            logger.info(f"Macro '{macro_id}' congelado")
    
    def unfreeze_macro(self, macro_id: str):
        """Descongela un macro"""
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no existe")
            return
            
        self.playback_manager.unfreeze_trajectory(macro_id)
        logger.info(f"Macro '{macro_id}' descongelado")
    
    def update_trajectory_speed(self, macro_id: str, speed: float):
        """
        Actualiza la velocidad de una trayectoria en vivo
        
        Args:
            macro_id: ID del macro
            speed: Nueva velocidad (-10 a 10)
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no existe")
            return
            
        macro = self._macros[macro_id]
        if not macro.trajectory_component or not macro.trajectory_component.enabled:
            logger.error(f"Macro {macro_id} no tiene trayectoria activa")
            return
            
        # Actualizar velocidad en el componente
        macro.trajectory_component.speed = abs(speed)
        
        # Actualizar en el playback controller si existe
        controller = self.playback_manager.get_controller(macro_id)
        if controller:
            controller.base_speed = speed
            
        logger.info(f"Velocidad de trayectoria actualizada a {speed} para macro '{macro_id}'")
    
    def update_trajectory_scale(self, macro_id: str, scale: float):
        """
        Actualiza la escala/tamaño de una trayectoria en vivo
        
        Args:
            macro_id: ID del macro
            scale: Nueva escala/tamaño en metros
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no existe")
            return
            
        macro = self._macros[macro_id]
        if not macro.trajectory_component or not macro.trajectory_component.enabled:
            logger.error(f"Macro {macro_id} no tiene trayectoria activa")
            return
            
        # Obtener tipo de trayectoria actual
        traj_type = getattr(macro.trajectory_component.trajectory_func, 'trajectory_type', None)
        if not traj_type:
            logger.error("No se puede determinar el tipo de trayectoria")
            return
            
        # Preservar fase y velocidad actual
        current_phase = macro.trajectory_component.phase
        current_speed = macro.trajectory_component.speed
        
        # Determinar parámetros según tipo
        params = {"speed": current_speed}
        
        if traj_type in ["circle", "spiral", "helix"]:
            params["radius"] = scale
        elif traj_type in ["figure8", "lissajous", "random"]:
            params["scale"] = scale
        elif traj_type == "line":
            # Para línea, escalar la longitud manteniendo dirección
            params["start"] = np.array([0.0, 0.0, 0.0])
            params["end"] = np.array([scale, 0.0, 0.0])
        elif traj_type == "wave":
            params["length"] = scale
        elif traj_type == "torus_knot":
            params["major_radius"] = scale
            params["minor_radius"] = scale * 0.4  # Proporción fija
            
        # Recrear la función de trayectoria con nuevos parámetros
        try:
            from trajectory_hub.core.trajectory_functions import create_trajectory_function
            new_func = create_trajectory_function(traj_type, **params)
            macro.trajectory_component.trajectory_func = new_func
            
            # Restaurar fase
            macro.trajectory_component.phase = current_phase
            
            logger.info(f"Escala de trayectoria actualizada a {scale}m para macro '{macro_id}'")
        except Exception as e:
            logger.error(f"Error actualizando escala: {e}")
    
    def update_trajectory_params(self, macro_id: str, **params):
        """
        Actualiza parámetros específicos de una trayectoria
        
        Args:
            macro_id: ID del macro
            **params: Parámetros a actualizar
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no existe")
            return
            
        macro = self._macros[macro_id]
        if not macro.trajectory_component or not macro.trajectory_component.enabled:
            logger.error(f"Macro {macro_id} no tiene trayectoria activa")
            return
            
        # Obtener tipo y parámetros actuales
        traj_type = getattr(macro.trajectory_component.trajectory_func, 'trajectory_type', None)
        if not traj_type:
            logger.error("No se puede determinar el tipo de trayectoria")
            return
            
        # Preservar estado actual
        current_phase = macro.trajectory_component.phase
        current_speed = macro.trajectory_component.speed
        
        # Merge con parámetros actuales (esto requeriría guardar los parámetros originales)
        # Por ahora, usar los nuevos parámetros con velocidad preservada
        params["speed"] = current_speed
        
        # Recrear la función
        try:
            from trajectory_hub.core.trajectory_functions import create_trajectory_function
            new_func = create_trajectory_function(traj_type, **params)
            macro.trajectory_component.trajectory_func = new_func
            macro.trajectory_component.phase = current_phase
            
            logger.info(f"Parámetros de trayectoria actualizados para macro '{macro_id}'")
        except Exception as e:
            logger.error(f"Error actualizando parámetros: {e}")
    
    def set_macro_rotation(self, macro_name, speed_x=0.0, speed_y=0.0, speed_z=0.0, center=None):
        """Configura rotación algorítmica para un macro con sistema de deltas"""
        if macro_name not in self._macros:
            print(f"❌ Macro '{macro_name}' no existe")
            return False
            
        macro = self._macros[macro_name]
        source_ids = list(macro.source_ids)
        
        # Centro por defecto es el centroide del macro
        if center is None:
            positions = []
            for sid in source_ids:
                if sid < len(self._positions):
                    positions.append(self._positions[sid].copy())
            if positions:
                center = np.mean(positions, axis=0)
            else:
                center = np.array([0.0, 0.0, 0.0])
        
        # Convertir center a array numpy si no lo es
        center = np.array(center, dtype=np.float32)
        
        # Configurar rotación para cada fuente del macro
        configured = 0
        for sid in source_ids:
            if sid in self.motion_states:
                motion = self.motion_states[sid]
                
                # Crear componente si no existe
                if 'macro_rotation' not in motion.active_components:
                    rotation = MacroRotation()
                    motion.active_components['macro_rotation'] = rotation
                else:
                    rotation = motion.active_components['macro_rotation']
                
                # Configurar rotación directamente
                rotation.speed_x = speed_x
                rotation.speed_y = speed_y
                rotation.speed_z = speed_z
                
                # Resetear ángulos acumulados cuando se cambian las velocidades
                rotation.angle_x = 0.0
                rotation.angle_y = 0.0
                rotation.angle_z = 0.0
                
                if center is not None:
                    rotation.center = center
                rotation.enabled = (
                    abs(float(speed_x)) > 0.001 or
                    abs(float(speed_y)) > 0.001 or
                    abs(float(speed_z)) > 0.001
                )
                configured += 1
        
        if configured > 0:
            print(f"✅ Rotación configurada para '{macro_name}'")
            print(f"   Centro: [{center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f}]")
            print(f"   Velocidades: X={float(speed_x):.2f}, Y={float(speed_y):.2f}, Z={float(speed_z):.2f} rad/s")
            print(f"   Fuentes: {configured}/{len(source_ids)}")
            return True
        
        return False


    def set_manual_macro_rotation(self, macro_id: str, pitch: float = None, 
                                 yaw: float = None, roll: float = None,
                                 interpolation_speed: float = 0.1,
                                 center: np.ndarray = None):
        """
        Configura rotación manual para un macro
        
        Args:
            macro_id: ID del macro
            pitch: Ángulo de pitch en radianes
            yaw: Ángulo de yaw en radianes
            roll: Ángulo de roll en radianes
            interpolation_speed: Velocidad de interpolación (0-1)
            center: Centro de rotación [x,y,z]
        """
        if macro_id not in self._macros:
            print(f"Macro '{macro_id}' no encontrado")
            return False
        
        macro = self._macros[macro_id]
        
        # Importar la clase
        from .motion_components import ManualMacroRotation
        
        # Configurar para cada fuente del macro
        for source_id in macro.source_ids:
            if source_id not in self.motion_states:
                continue
            
            motion = self.motion_states[source_id]
            
            # Crear o actualizar el componente
            if 'manual_macro_rotation' not in motion.active_components:
                rotation = ManualMacroRotation()
                motion.active_components['manual_macro_rotation'] = rotation
            else:
                rotation = motion.active_components['manual_macro_rotation']
            
            # Configurar parámetros
            rotation.set_target_rotation(pitch, yaw, roll)
            rotation.set_interpolation_speed(interpolation_speed)
            
            if center is not None:
                rotation.center = center.copy()
            else:
                # Usar el centro del macro
                positions = [self._positions[sid] for sid in macro.source_ids 
                           if sid < len(self._positions)]
                if positions:
                    rotation.center = np.mean(positions, axis=0)
            
            rotation.enabled = True
        
        print(f"✅ Rotación manual configurada para macro '{macro_id}'")
        return True
    
    def set_individual_rotation(self, source_id: int, 
                              speed_x: float = 0.0, speed_y: float = 0.0, speed_z: float = 0.0,
                              center: Optional[List[float]] = None) -> bool:
        """
        Configura rotación algorítmica continua para una fuente individual
        
        Args:
            source_id: ID de la fuente
            speed_x: Velocidad de rotación en X (rad/s)
            speed_y: Velocidad de rotación en Y (rad/s)
            speed_z: Velocidad de rotación en Z (rad/s)
            center: Centro de rotación (opcional, default: posición actual)
            
        Returns:
            True si se configuró correctamente
        """
        if source_id not in self.motion_states:
            print(f"❌ Fuente {source_id} no existe")
            return False
        
        motion = self.motion_states[source_id]
        
        # Determinar centro
        if center is None:
            center = self._positions[source_id].copy()
        else:
            center = np.array(center, dtype=np.float32)
        
        # Crear o actualizar componente
        from trajectory_hub.core.motion_components import IndividualRotation
        
        if 'individual_rotation' in motion.active_components:
            # Actualizar existente
            rotation = motion.active_components['individual_rotation']
            rotation.set_rotation_speeds(speed_x, speed_y, speed_z)
            rotation.center = center
        else:
            # Crear nuevo
            rotation = IndividualRotation(center=center, speed_x=speed_x, speed_y=speed_y, speed_z=speed_z)
            motion.active_components['individual_rotation'] = rotation
        
        print(f"✅ Rotación algorítmica configurada para fuente {source_id}")
        print(f"   Velocidades: X={speed_x:.3f}, Y={speed_y:.3f}, Z={speed_z:.3f} rad/s")
        
        return True
    
    def set_manual_individual_rotation(self, source_id: int,
                                     yaw: float = 0.0, pitch: float = 0.0, roll: float = 0.0,
                                     interpolation_speed: float = 0.1,
                                     center: Optional[List[float]] = None) -> bool:
        """
        Configura rotación manual con interpolación para una fuente individual
        
        Args:
            source_id: ID de la fuente
            yaw: Rotación objetivo en Y (radianes)
            pitch: Rotación objetivo en X (radianes)
            roll: Rotación objetivo en Z (radianes)
            interpolation_speed: Velocidad de interpolación (0.01 a 1.0)
            center: Centro de rotación (opcional, default: posición actual)
            
        Returns:
            True si se configuró correctamente
        """
        if source_id not in self.motion_states:
            print(f"❌ Fuente {source_id} no existe")
            return False
        
        motion = self.motion_states[source_id]
        
        # Determinar centro
        if center is None:
            center = self._positions[source_id].copy()
        else:
            center = np.array(center, dtype=np.float32)
        
        # Crear o actualizar componente
        from trajectory_hub.core.motion_components import ManualIndividualRotation
        
        if 'manual_individual_rotation' in motion.active_components:
            # Actualizar existente
            rotation = motion.active_components['manual_individual_rotation']
            rotation.center = center
            rotation.set_target_rotation(yaw, pitch, roll, interpolation_speed)
            # Sincronizar con estado actual
            rotation._sync_with_state(motion.state)
        else:
            # Crear nuevo
            rotation = ManualIndividualRotation()
            rotation.set_target_rotation(yaw, pitch, roll, interpolation_speed)
            rotation._sync_with_state(motion.state)
            motion.active_components['manual_individual_rotation'] = rotation
        
        print(f"✅ Rotación manual configurada para fuente {source_id}")
        print(f"   Objetivos: Yaw={math.degrees(yaw):.1f}°, Pitch={math.degrees(pitch):.1f}°, Roll={math.degrees(roll):.1f}°")
        
        return True
    
    def stop_individual_rotation(self, source_id: int, rotation_type: str = 'both') -> bool:
        """
        Detiene la rotación de una fuente individual
        
        Args:
            source_id: ID de la fuente
            rotation_type: 'algorithmic', 'manual', o 'both'
            
        Returns:
            True si se detuvo correctamente
        """
        if source_id not in self.motion_states:
            print(f"❌ Fuente {source_id} no existe")
            return False
        
        motion = self.motion_states[source_id]
        stopped = False
        
        if rotation_type in ['algorithmic', 'both']:
            if 'individual_rotation' in motion.active_components:
                motion.active_components['individual_rotation'].enabled = False
                print(f"✅ Rotación algorítmica detenida para fuente {source_id}")
                stopped = True
        
        if rotation_type in ['manual', 'both']:
            if 'manual_individual_rotation' in motion.active_components:
                motion.active_components['manual_individual_rotation'].enabled = False
                print(f"✅ Rotación manual detenida para fuente {source_id}")
                stopped = True
        
        return stopped
    
    def set_batch_individual_rotation(self, source_ids: List[int], 
                                    speed_x: float = 0.0, speed_y: float = 0.0, speed_z: float = 0.0,
                                    offset_factor: float = 0.0) -> int:
        """
        Configura rotación algorítmica para múltiples fuentes con desfase opcional
        
        Args:
            source_ids: Lista de IDs de fuentes
            speed_x: Velocidad base en X (rad/s)
            speed_y: Velocidad base en Y (rad/s)
            speed_z: Velocidad base en Z (rad/s)
            offset_factor: Factor de desfase entre fuentes (0.0 = sin desfase)
            
        Returns:
            Número de fuentes configuradas exitosamente
        """
        configured = 0
        
        for i, sid in enumerate(source_ids):
            # Aplicar desfase si se especifica
            factor = 1.0 + (i * offset_factor)
            sx = speed_x * factor
            sy = speed_y * factor
            sz = speed_z * factor
            
            if self.set_individual_rotation(sid, sx, sy, sz):
                configured += 1
        
        print(f"Rotacion configurada para {configured}/{len(source_ids)} fuentes")
        return configured
    
    def toggle_manual_macro_rotation(self, macro_id: str, enabled: bool = None):
        """Activa/desactiva la rotación manual de un macro"""
        if macro_id not in self._macros:
            return False
        
        macro = self._macros[macro_id]
        
        for source_id in macro.source_ids:
            if source_id in self.motion_states:
                motion = self.motion_states[source_id]
                if 'manual_macro_rotation' in motion.active_components:
                    comp = motion.active_components['manual_macro_rotation']
                    if enabled is None:
                        comp.enabled = not comp.enabled
                    else:
                        comp.enabled = enabled
        
        return True

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
        if source_id not in self.motion_states:
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
        
        # Aplicar inmediatamente si hay una trayectoria individual
        motion = self._source_motions[source_id]
        traj = motion.components.get('individual_trajectory')
        if traj:
            # Guardar la matriz de rotación en el componente
            traj.rotation_matrix = self.trajectory_rotations[source_id]['matrix']
            
            # Si la trayectoria tiene set_rotation, usarlo
            if hasattr(traj, 'set_rotation'):
                traj.set_rotation(pitch, yaw, roll, enabled=True)
        
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
    
    def _evaluate_custom_formation(self, t: float, i: int, n: int) -> Tuple[float, float, float]:
        """
        Evalúa una formación personalizada basada en funciones matemáticas
        
        Parameters
        ----------
        t : float
            Parámetro normalizado [0, 1]
        i : int
            Índice de la fuente actual
        n : int
            Número total de fuentes
            
        Returns
        -------
        Tuple[float, float, float]
            Coordenadas (x, y, z)
        """
        import math
        
        # Contexto seguro para evaluar expresiones
        safe_context = {
            't': t,
            'i': i,
            'n': n,
            'pi': math.pi,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'abs': abs,
            'exp': math.exp,
            'log': math.log,
            'pow': pow
        }
        
        # Valores por defecto
        x, y, z = 0.0, 0.0, 0.0
        
        if not hasattr(self, '_custom_formation_function'):
            return (x, y, z)
            
        func = self._custom_formation_function
        
        try:
            # Si se especificó modo polar
            if func.get('polar', False) and 'r' in func:
                # Evaluar radio
                r = eval(func['r'], {"__builtins__": {}}, safe_context)
                # Theta es simplemente t * 2π por defecto
                theta = t * 2 * math.pi
                
                # En modo polar, x,y se calculan desde r y theta
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                    
                # Z se evalúa normalmente
                z = eval(func.get('z', '0'), {"__builtins__": {}}, safe_context)
            else:
                # Modo cartesiano directo
                x = eval(func.get('x', '0'), {"__builtins__": {}}, safe_context)
                y = eval(func.get('y', '0'), {"__builtins__": {}}, safe_context)
                z = eval(func.get('z', '0'), {"__builtins__": {}}, safe_context)
                
        except Exception as e:
            logger.error(f"Error evaluando formación personalizada: {e}")
            # Fallback a círculo
            angle = t * 2 * math.pi
            x = math.cos(angle)
            y = math.sin(angle)
            z = 0
            
        return (x, y, z)
    
    def adjust_macro_spacing(self, macro_id: str, new_spacing: float):
        """
        Ajusta el spacing de un macro existente, recalculando las posiciones
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        new_spacing : float
            Nuevo valor de spacing
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no existe")
            return False
            
        macro = self._macros[macro_id]
        
        # Obtener información de la formación actual
        if not hasattr(macro, 'formation') or not hasattr(macro, 'source_ids'):
            logger.error(f"Macro {macro_id} no tiene información de formación")
            return False
            
        # Guardar formación y función personalizada si existe
        formation = getattr(macro, 'formation', 'circle')
        custom_function = getattr(macro, 'custom_function', None)
        
        # Obtener el centro actual antes de reaplicar la formación
        current_center = self.get_macro_center(macro_id)
        if current_center is None:
            current_center = np.array([0.0, 0.0, 0.0])
            
        # Si había función personalizada, guardarla temporalmente
        if custom_function:
            self._custom_formation_function = custom_function
            
        # Reaplicar la formación con el nuevo spacing y el centro actual
        source_ids = list(macro.source_ids)
        self._apply_formation(source_ids, formation, new_spacing, center=current_center)
        
        # Limpiar función personalizada
        if hasattr(self, '_custom_formation_function'):
            delattr(self, '_custom_formation_function')
            
        # Actualizar el spacing guardado en el macro
        macro.spacing = new_spacing
        
        logger.info(f"Spacing del macro {macro_id} ajustado a {new_spacing}")
        return True
    
    def move_macro_center(self, macro_id: str, new_center: np.ndarray):
        """
        Mueve el centro de un macro a una nueva posición
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        new_center : np.ndarray
            Nueva posición del centro [x, y, z]
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no existe")
            return False
            
        macro = self._macros[macro_id]
        source_ids = list(macro.source_ids)
        
        if not source_ids:
            return False
            
        # Calcular centro actual
        current_positions = []
        for sid in source_ids:
            if sid < len(self._positions):
                current_positions.append(self._positions[sid].copy())
                
        if not current_positions:
            return False
            
        current_center = np.mean(current_positions, axis=0)
        
        # Calcular desplazamiento
        offset = new_center - current_center
        
        # Mover todas las fuentes
        for sid in source_ids:
            if sid in self._source_motions:
                motion = self._source_motions[sid]
                # Actualizar posición
                motion.state.position += offset
                self._positions[sid] = motion.state.position.copy()
                
                # Actualizar base_position si tiene trayectoria individual
                if 'individual_trajectory' in motion.components:
                    traj = motion.components['individual_trajectory']
                    if hasattr(traj, 'base_position'):
                        traj.base_position += offset
                        
        logger.info(f"Macro {macro_id} movido a {new_center}")
        return True
    
    def get_macro_center(self, macro_id: str) -> Optional[np.ndarray]:
        """
        Obtiene el centro actual de un macro
        
        Parameters
        ----------
        macro_id : str
            ID del macro
            
        Returns
        -------
        np.ndarray or None
            Centro del macro [x, y, z] o None si no existe
        """
        if macro_id not in self._macros:
            return None
            
        macro = self._macros[macro_id]
        source_ids = list(macro.source_ids)
        
        positions = []
        for sid in source_ids:
            if sid < len(self._positions):
                positions.append(self._positions[sid])
                
        if not positions:
            return None
            
        return np.mean(positions, axis=0)
    
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


    # =========== SISTEMA DE CONCENTRACIÓN ===========
    
    def set_macro_concentration(self, macro_name: str, factor: float = 0.5):
        """Aplica concentración usando sistema de deltas"""
        # Buscar el macro
        full_name = None
        for name in self._macros.keys():
            if name.endswith(f"_{macro_name}") or name == macro_name:
                full_name = name
                break
                
        if not full_name:
            print(f"Macro {macro_name} no encontrado")
            return False
            
        macro = self._macros[full_name]
        print(f"Aplicando concentración a macro {full_name} con factor {factor}")
        
        # Crear/actualizar componente de concentración para cada fuente
        from trajectory_hub.core.motion_components import ConcentrationComponent
        
        for sid in macro.source_ids:
            # Asegurar que existe motion state
            if sid not in self.motion_states:
                from trajectory_hub.core.motion_components import SourceMotion
                self.motion_states[sid] = SourceMotion(sid)
            
            motion = self.motion_states[sid]
            
            # Buscar o crear componente de concentración
            concentration = None
            for comp in motion.active_components:
                if isinstance(comp, ConcentrationComponent):
                    concentration = comp
                    break
            
            if concentration is None:
                concentration = ConcentrationComponent()
                concentration.macro = macro
                concentration.enabled = True
                motion.add_component(concentration)
                print(f"   Añadido ConcentrationComponent a source {sid}")
            
            # Configurar
            concentration.enabled = True
            concentration.concentration_factor = factor
            concentration.macro_center = np.mean([self._positions[i] for i in macro.source_ids], axis=0)
            print(f"   Source {sid}: factor={factor}, centro={concentration.macro_center}")
        
        return True
    def animate_macro_concentration(self, macro_id: str, target_factor: float,
                                   duration: float = 2.0, 
                                   curve: str = "ease_in_out") -> bool:
        """Animar transición de concentración"""
        macro = self._macros.get(macro_id)
        if not macro:
            return False
            
        # Importar necesario
        from trajectory_hub.core.motion_components import MotionDelta, ConcentrationCurve
            
        # Convertir string a enum
        curve_enum = ConcentrationCurve[curve.upper().replace(" ", "_")]
        
        for sid in macro.source_ids:
            if sid in self._source_motions:
                concentration = self._source_motions[sid].components.get('concentration')
                if concentration:
                    concentration.animation_curve = curve_enum
                    
        return self.set_macro_concentration(macro_id, target_factor, duration)
        
    def get_macro_concentration_state(self, macro_id: str) -> Dict:
        """Obtener estado actual de concentración"""
        macro = self._macros.get(macro_id)
        if not macro or not macro.source_ids:
            return {"error": "Macro no encontrado"}
            
        # Obtener del primer source
        first_sid = next(iter(macro.source_ids))
        if first_sid not in self._source_motions:
            return {"error": "Source no encontrado"}
            
        concentration = self._source_motions[first_sid].components.get('concentration')
        if not concentration:
            return {
                "enabled": False,
                "factor": 1.0,
                "mode": "fixed_point",
                "animating": False
            }
            
        return {
            "enabled": concentration.enabled,
            "factor": concentration.factor,
            "mode": concentration.mode.value,
            "animating": concentration.animation_active,
            "target_point": concentration.target_point.tolist(),
            "include_macro_trajectory": concentration.include_macro_trajectory
        }
        
    def toggle_macro_concentration(self, macro_id: str) -> bool:
        """Alternar entre concentrado y disperso"""
        state = self.get_macro_concentration_state(macro_id)
        if state.get("error"):
            return False
            
        current_factor = state.get("factor", 1.0)
        target_factor = 0.0 if current_factor > 0.5 else 1.0
        
        return self.animate_macro_concentration(macro_id, target_factor, 2.0)
        
    def set_concentration_parameters(self, macro_id: str, **params) -> bool:
        """Configurar parámetros avanzados de concentración"""
        macro = self._macros.get(macro_id)
        if not macro:
            return False
            
        for sid in macro.source_ids:
            if sid in self._source_motions:
                concentration = self._source_motions[sid].components.get('concentration')
                if concentration:
                    for key, value in params.items():
                        if hasattr(concentration, key):
                            setattr(concentration, key, value)
                            
        return True

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

    def update(self, dt: float = None) -> None:
        """Actualiza el sistema completo con soporte para deltas"""
        if dt is None:
            current_time = time.time()
            dt = current_time - self._last_time
            self._last_time = current_time
        else:
            current_time = self._last_time + dt
            self._last_time = current_time
        
        # Rate limiting
        if not self._check_rate_limit():
            if self.osc_bridge and hasattr(self, '_active_sources') and self._active_sources:
                positions = {}  # Cambiar a diccionario
                for source_id in sorted(self._active_sources.keys()):
                    source = self._active_sources[source_id]
                    if hasattr(source, 'position') and source.position is not None:
                        pos = source.position
                        positions[source_id] = (float(pos[0]), float(pos[1]), float(pos[2]))
            
                if positions:
                    self.osc_bridge.send_source_positions(positions)
            return
        
        # 1. ACTUALIZAR COMPONENTES DE MOVIMIENTO (motion_states)
        for source_id, motion in self.motion_states.items():

            # Sincronizar state con position
            if source_id in self._active_sources:
                motion.state.position = self._positions[source_id].copy()
            if motion is not None:
                # Actualizar el SourceMotion con el tiempo actual
                # motion.update(current_time, dt)  # REEMPLAZADO
                # Usar update_with_deltas para obtener deltas
                if hasattr(motion, 'update_with_deltas'):
                    deltas = motion.update_with_deltas(current_time, dt)
                    # Aplicar deltas
                    for delta in deltas:
                        if delta.source_id in self._positions:
                            self._positions[delta.source_id] += delta.position
                        if delta.source_id in self.motion_states:
                            state = self.motion_states[delta.source_id].state
                            state.position[:] = self._positions[delta.source_id]
                            state.orientation += delta.orientation
                            if hasattr(delta, 'aperture') and delta.aperture is not None:
                                state.aperture = delta.aperture
                

# Enviar posiciones OSC al final de cada update
        if self.osc_bridge and hasattr(self, '_positions') and hasattr(self, '_active_sources'):
            if self._active_sources and len(self._positions) > 0:
                positions = {}  # Cambiar a diccionario
                for source_id in sorted(self._active_sources):
                    if source_id < len(self._positions):
                        pos = self._positions[source_id]
                        positions[source_id] = (float(pos[0]), float(pos[1]), float(pos[2]))
                
                if positions:
                    self.osc_bridge.send_source_positions(positions)
        if self.osc_bridge and hasattr(self, '_positions') and self._positions is not None:
            positions_to_send = {}
            # _positions es un numpy array, necesitamos las sources activas
            if hasattr(self, '_active_sources') and self._active_sources:
                for source_id in self._active_sources:
                    if source_id < len(self._positions) and source_id < self.config.get('n_sources', 100):
                        pos = self._positions[source_id]
                        positions_to_send[source_id] = (
                            float(pos[0]) if len(pos) > 0 else 0.0,
                            float(pos[1]) if len(pos) > 1 else 0.0,
                            float(pos[2]) if len(pos) > 2 else 0.0
                        )
            else:
                # Si no hay _active_sources, enviar las primeras N posiciones no-cero
                n_sources = min(len(self._positions), self.config.get('n_sources', 999))
                for i in range(n_sources):
                    pos = self._positions[i]
                    # Solo enviar si la posición no es cero
                    if hasattr(pos, '__len__') and any(p != 0 for p in pos):
                        positions_to_send[i] = (
                            float(pos[0]) if len(pos) > 0 else 0.0,
                            float(pos[1]) if len(pos) > 1 else 0.0,
                            float(pos[2]) if len(pos) > 2 else 0.0
                        )
            
            if positions_to_send:
                print(f"   📡 Enviando {len(positions_to_send)} posiciones a Spat")
                self.osc_bridge.send_source_positions(positions_to_send)

                # Obtener el estado actualizado
                state = motion.state
                
                # Actualizar posición en el array principal
                if source_id < len(self._positions):
                    self._positions[source_id] = state.position
                    
                    # Si hay orientación en el estado, actualizar también
                    if hasattr(state, 'orientation') and state.orientation is not None:
                        if source_id < len(self._orientations):
                            self._orientations[source_id] = state.orientation
        
        # 2. PROCESAR DELTAS (si está implementado)
        if hasattr(self, '_process_deltas'):
            self._process_deltas(current_time, dt)
        
        # 3. ACTUALIZAR MODULADORES DE ORIENTACIÓN
        if self.enable_modulator:
            for source_id, state in self.motion_states.items():
                if source_id in self.orientation_modulators:
                    modulator = self.orientation_modulators[source_id]
                    if modulator.enabled:
                        # Actualizar estado con modulación
                        state = modulator.update(state, current_time, dt)
                        self.motion_states[source_id].state = state
                        
                        # Actualizar arrays principales
                        if source_id < len(self._orientations):
                            self._orientations[source_id] = state.orientation
                        if source_id < len(self._apertures):
                            self._apertures[source_id] = state.aperture
        
        # 4. APLICAR FÍSICA Y OTROS SISTEMAS
        # ... (mantener código existente de física si existe)
        
        # 5. ENVIAR ACTUALIZACIONES OSC
        # self\.send_osc_update\(\)  # Temporalmente comentado
        
        # Incrementar contador de frames
        self._frame_count += 1
        self._time += dt

        # Enviar actualizaciones OSC
        self._send_osc_update()

        # FORCE: Enviar OSC al final de update
        try:
            if self.osc_bridge and hasattr(self, '_positions') and hasattr(self, '_active_sources'):
                positions = {}
                for sid in list(self._active_sources):  # Max 16 sources
                    if sid < len(self._positions):
                        pos = self._positions[sid]
                        positions[sid] = (float(pos[0]), float(pos[1]), float(pos[2]))
                if positions:
                    self.osc_bridge.send_source_positions(positions)
                    # print(f"✅ OSC enviado: {len(positions)} fuentes")  # Descomentar para debug
        except Exception as e:
            pass  # Silencioso para no interrumpir


        # Enviar posiciones OSC al final de cada update
        if self.osc_bridge and self._active_sources and hasattr(self, '_sources'):
            positions = {}  # Cambiar a diccionario
            for source_id in sorted(self._active_sources):
                if source_id in self._sources:
                    source = self._sources[source_id]
                    if hasattr(source, 'position') and source.position is not None:
                        pos = source.position
                        # source_id es 0-based, se convertirá a 1-based en send_source_positions
                        positions[source_id] = (float(pos[0]), float(pos[1]), float(pos[2]))
            
            if positions:
                self.osc_bridge.send_source_positions(positions)


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

    def step(self) -> None:
        """Ejecuta un paso de simulación con soporte de deltas"""
        if not self.running:
            return
        
        current_time = time.time()
        dt = 1.0 / self.fps
        
        # Sistema de deltas para composición de movimientos
        all_deltas = []
        
        # Actualizar cada SourceMotion y recolectar deltas
        for source_id, motion in self.motion_states.items():
            if hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(current_time, dt)
                if deltas:
                    all_deltas.extend(deltas)
        
        # Aplicar todos los deltas a las posiciones
        for delta in all_deltas:
            # No usar delta.source_id aquí - se procesa más adelante
                if delta.position is not None:
                    self._positions[delta.source_id] += delta.position
        
        # Llamar a update si existe para mantener compatibilidad
        if hasattr(self, 'update'):
            self.update()


    def step(self) -> None:
        """Ejecuta un paso de simulación con soporte de deltas"""
        if not self.running:
            return
        
        current_time = time.time()
        dt = 1.0 / self.fps
        
        # Sistema de deltas para composición de movimientos
        all_deltas = []
        
        # Actualizar cada SourceMotion y recolectar deltas
        for source_id, motion in self.motion_states.items():
            if hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(current_time, dt)
                if deltas:
                    all_deltas.extend(deltas)
        
        # Aplicar todos los deltas a las posiciones
        for delta in all_deltas:
            # No usar delta.source_id aquí - se procesa más adelante
                if delta.position is not None:
                    self._positions[delta.source_id] += delta.position
        
        # Llamar a update si existe para mantener compatibilidad
        if hasattr(self, 'update'):
            self.update()


    def step(self) -> Dict[str, Any]:
        """
        Método de compatibilidad para InteractiveController
        Llama a update() y devuelve el estado
        """
        return self.update()

    def get_debug_info(self, source_id: int) -> Dict[str, Any]:
        """Obtener información de debug de una fuente"""
        if source_id not in self.motion_states:
            return {"error": "Fuente no encontrada"}
            
        motion = self._source_motions[source_id]
        info = {
            "id": source_id,
            "position": motion.state.position.tolist(),
            "orientation": motion.state.orientation.tolist(),
            "aperture": motion.state.aperture,
            "components": {}
        }
        
        for name, component in motion.components.items():
            comp_info = {
                "enabled": component.enabled,
                "weight": component.weight
            }
            
            if isinstance(component, IndividualTrajectory):
                comp_info.update({
                    "shape": component.shape_type,
                    "movement_mode": component.movement_mode.value,
                    "position_on_trajectory": component.position_on_trajectory
                })
            elif isinstance(component, TrajectoryTransform):
                comp_info.update({
                    "displacement_mode": component.displacement_mode.value,
                    "offset": component.offset.tolist() if isinstance(component.offset, np.ndarray) else str(component.offset)
                })
            elif isinstance(component, OrientationModulation):
                comp_info.update({
                    "has_yaw": component.yaw_func is not None,
                    "has_pitch": component.pitch_func is not None,
                    "has_roll": component.roll_func is not None
                })
                
            info["components"][name] = comp_info
            
        return info

    # ========== MÉTODOS DE COMPATIBILIDAD ==========
    
    def set_source_name(self, source_id: int, name: str):
        """Compatibilidad: establecer nombre de fuente"""
        if source_id in self._source_info:
            self._source_info[source_id].name = name
        else:
            logger.warning(f"Fuente {source_id} no existe para establecer nombre")
    
    def get_source_names(self) -> Dict[int, str]:
        """Compatibilidad: obtener nombres de fuentes"""
        return {sid: info.name for sid, info in self._source_info.items() if info.name}

    def get_deformer(self, macro_id: Optional[str] = None) -> CompositeDeformer:
        """
        Obtener deformador para un macro o el global
        
        Parameters
        ----------
        macro_id : str, optional
            ID del macro. Si None, retorna el deformador global
            
        Returns
        -------
        CompositeDeformer
            Deformador solicitado
        """
        if macro_id:
            if macro_id not in self._macro_deformers:
                self._macro_deformers[macro_id] = CompositeDeformer()
            return self._macro_deformers[macro_id]
        return self.global_deformer

    def save_modulator_state(self, macro_name: str) -> Dict[str, Any]:
        """Guardar estado de los moduladores de un macro"""
        if macro_name not in self._macros:
            logger.error(f"Macro '{macro_name}' no encontrado")
            return {}
            
        macro = self._macros[macro_name]
        state = {}
        
        for sid in macro.source_ids:
            if sid in self.orientation_modulators:
                state[sid] = self.orientation_modulators[sid].get_state_dict()
                
        logger.info(f"Estado de moduladores guardado para macro '{macro_name}'")
        return state

    def load_modulator_state(self, macro_name: str, state: Dict[str, Any]) -> bool:
        """Cargar estado de los moduladores de un macro"""
        if macro_name not in self._macros:
            logger.error(f"Macro '{macro_name}' no encontrado")
            return False
            
        macro = self._macros[macro_name]
        
        for sid, mod_state in state.items():
            sid = int(sid)  # Asegurar que es int
            if sid not in macro.source_ids:
                continue
                
            if sid not in self.orientation_modulators:
                self.create_orientation_modulator(sid)
                
            self.orientation_modulators[sid].load_state_dict(mod_state)
            
        logger.info(f"Estado de moduladores cargado para macro '{macro_name}'")
        return True


    def get_orientation_presets(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtener diccionario de presets de orientación disponibles
        
        Returns
        -------
        dict
            Diccionario con información de cada preset
        """
        # Importar la clase si no está importada
        try:
            from trajectory_hub.core.motion_components import MotionDelta, AdvancedOrientationModulation
        except ImportError:
            from motion_components import AdvancedOrientationModulation
        
        # Crear una instancia temporal para acceder a los presets
        temp_modulator = AdvancedOrientationModulation()
        presets = temp_modulator.presets
        
        # Formatear para el usuario
        formatted_presets = {}
        for name, data in presets.items():
            formatted_presets[name] = {
                "description": data["description"],
                "shape": data["shape"],
                "lfo": data["lfo"],
                "aperture": data["aperture"],
                "aperture_mod": data.get("aperture_mod", 0.0)
            }
            
        return formatted_presets

    def get_modulator_state(self, source_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtener estado actual del modulador de una fuente
        
        Parameters
        ----------
        source_id : int
            ID de la fuente
            
        Returns
        -------
        dict or None
            Estado del modulador o None si no existe
        """
        if source_id not in self.orientation_modulators:
            return None
            
        modulator = self.orientation_modulators[source_id]
        
        return {
            "enabled": modulator.enabled,
            "intensity": modulator.intensity,
            "modulation_shape": modulator.modulation_shape,
            "lfo_frequency": modulator.lfo_frequency,
            "aperture_base": modulator.aperture_base,
            "aperture_modulation": modulator.aperture_modulation,
            "time_offset": modulator.time_offset
        }

    def set_orientation_lfo(self, macro_id: str, frequency: float) -> bool:
        """
        Establecer frecuencia LFO del modulador
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        frequency : float
            Frecuencia en Hz (0.1-10)
            
        Returns
        -------
        bool
            True si se aplicó correctamente
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no encontrado")
            return False
            
        macro = self._macros[macro_id]
        frequency = np.clip(frequency, 0.1, 10.0)
        
        for sid in macro.source_ids:
            if sid in self.orientation_modulators:
                self.orientation_modulators[sid].lfo_frequency = frequency
                
        logger.info(f"LFO establecido a {frequency} Hz para macro {macro_id}")
        return True

    def set_orientation_intensity(self, macro_id: str, intensity: float) -> bool:
        """
        Establecer intensidad del modulador
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        intensity : float
            Intensidad (0.0-1.0)
            
        Returns
        -------
        bool
            True si se aplicó correctamente
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no encontrado")
            return False
            
        macro = self._macros[macro_id]
        intensity = np.clip(intensity, 0.0, 1.0)
        
        for sid in macro.source_ids:
            if sid in self.orientation_modulators:
                self.orientation_modulators[sid].intensity = intensity
                
        logger.info(f"Intensidad establecida a {intensity:.1%} para macro {macro_id}")
        return True

    def interpolate_orientation_presets(self, macro_id: str, preset1: str, preset2: str, factor: float) -> bool:
        """
        Interpolar entre dos presets de orientación
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        preset1 : str
            Nombre del primer preset
        preset2 : str
            Nombre del segundo preset
        factor : float
            Factor de interpolación (0.0 = preset1, 1.0 = preset2)
            
        Returns
        -------
        bool
            True si se aplicó correctamente
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no encontrado")
            return False
            
        macro = self._macros[macro_id]
        factor = np.clip(factor, 0.0, 1.0)
        
        for sid in macro.source_ids:
            if sid in self.orientation_modulators:
                self.orientation_modulators[sid].interpolate_presets(preset1, preset2, factor)
                
        logger.info(f"Interpolación {factor:.1%} entre '{preset1}' y '{preset2}'")
        return True

    def set_orientation_shape(self, macro_id: str, shape: str, scale: Optional[List[float]] = None) -> bool:
        """
        Configurar forma de modulación manualmente
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        shape : str
            Tipo de forma (circle, ellipse, lissajous, etc.)
        scale : list of float, optional
            Escala en cada eje [yaw, pitch, roll]
            
        Returns
        -------
        bool
            True si se aplicó correctamente
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no encontrado")
            return False
            
        macro = self._macros[macro_id]
        
        for sid in macro.source_ids:
            if sid in self.orientation_modulators:
                modulator = self.orientation_modulators[sid]
                modulator.modulation_shape = shape
                if scale:
                    modulator.shape_scale = np.array(scale)
                    
        logger.info(f"Forma '{shape}' configurada para macro {macro_id}")
        return True

    def toggle_orientation_modulation(self, macro_id: str, enabled: bool) -> bool:
        """
        Activar/desactivar modulación de orientación
        
        Parameters
        ----------
        macro_id : str
            ID del macro
        enabled : bool
            True para activar, False para desactivar
            
        Returns
        -------
        bool
            True si se aplicó correctamente
        """
        if macro_id not in self._macros:
            logger.error(f"Macro {macro_id} no encontrado")
            return False
            
        macro = self._macros[macro_id]
        
        for sid in macro.source_ids:
            if sid in self.orientation_modulators:
                self.orientation_modulators[sid].enabled = enabled
                
        state = "activada" if enabled else "desactivada"
        logger.info(f"Modulación {state} para macro {macro_id}")
        return True
    
    def _send_osc_update(self):
        """Envía actualizaciones OSC de todas las fuentes activas"""
        if not hasattr(self, 'osc_bridge') or self.osc_bridge is None:
            return
            
        for source_id in self._active_sources:
            if source_id in self._positions:
                pos = self._positions[source_id]
                
                # Enviar posición
                self.osc_bridge.send_position(
                    source_id=source_id,
                    x=float(pos[0]),
                    y=float(pos[1]),
                    z=float(pos[2])
                )
                
                # Enviar orientación si existe
                if hasattr(self, '_orientations') and source_id in self._orientations:
                    orient = self._orientations[source_id]
                    self.osc_bridge.send_orientation(
                        source_id=source_id,
                        yaw=float(orient.get('yaw', 0)),
                        pitch=float(orient.get('pitch', 0)),
                        roll=float(orient.get('roll', 0))
                    )
    
    def update(self, dt):
        """Actualiza el sistema completo"""
        current_time = time.time()
        dt = 1.0 / self.fps
        
        # Actualizar estados de movimiento con sistema de deltas
        for source_id, motion in self.motion_states.items():
            if source_id not in self._active_sources:
                continue
                
            # IMPORTANTE: Sincronizar estado con posición actual
            motion.state.position = self._positions[source_id].copy()
            
            # Obtener deltas de TODOS los componentes activos
            if hasattr(motion, 'update_with_deltas'):
                deltas = motion.update_with_deltas(current_time, dt)
                
                # Aplicar cada delta a la posición
                if deltas:
                    for delta in deltas:
                        if delta and delta.position is not None:
                            self._positions[source_id] += delta.position
                            
                            # Actualizar estado después del cambio
                            motion.state.position = self._positions[source_id].copy()
            
            # Actualizar el motion (para componentes sin deltas)
            if hasattr(motion, 'update'):
                motion.update(current_time, dt)
        
        # Actualizar moduladores de orientación si están habilitados
        if self.enable_modulator:
            for source_id, state in self.motion_states.items():
                if source_id in self.orientation_modulators:
                    modulator = self.orientation_modulators[source_id]
                    if modulator.enabled:
                        # Actualizar estado con modulación
                        state = modulator.update(state, current_time, dt)
                        self.motion_states[source_id] = state
        
        # Incrementar contador de frames y tiempo
        self._frame_count += 1
        self._time += dt
        
        # Enviar actualizaciones OSC con rate limiting
        # self\.send_osc_update\(\)  # Temporalmente comentado        # Enviar posiciones OSC
        if self.osc_bridge and hasattr(self, '_active_sources') and self._active_sources:
            if hasattr(self, '_positions') and len(self._positions) > 0:
                positions = {}  # Cambiar a diccionario
                for source_id in sorted(self._active_sources):
                    if source_id < len(self._positions):
                        pos = self._positions[source_id]
                        # source_id es 0-based, se convertirá a 1-based en send_source_positions
                        positions[source_id] = (float(pos[0]), float(pos[1]), float(pos[2]))
                
                if positions:
                    self.osc_bridge.send_source_positions(positions)
