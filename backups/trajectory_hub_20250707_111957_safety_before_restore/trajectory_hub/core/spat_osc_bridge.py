"""
spat_osc_bridge.py - Puente OSC robusto y optimizado para Spat Revolution
"""
from __future__ import annotations

import asyncio
import logging
import socket
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Sequence, List, Optional, Dict, Any, Union, Tuple
import numpy as np

logger = logging.getLogger(__name__)

try:
    from pythonosc import udp_client
    from pythonosc.osc_message_builder import OscMessageBuilder
    from pythonosc.osc_bundle_builder import OscBundleBuilder
    _OSC_AVAILABLE = True
except ImportError:
    logger.warning("python-osc no está instalado. Usando modo simulación.")
    _OSC_AVAILABLE = False
    
    # Stubs para desarrollo
    class MockUDPClient:
        def __init__(self, address: str, port: int):
            self.address = address
            self.port = port
            logger.info(f"MockUDPClient creado para {address}:{port}")
            
        def send_message(self, address: str, value: Any):
            logger.debug(f"[MOCK] {address} -> {value}")
            
        def send_bundle(self, bundle: Any):
            logger.debug(f"[MOCK] Bundle enviado")
    
    class udp_client:
        SimpleUDPClient = MockUDPClient


@dataclass
class OSCTarget:
    """Configuración robusta de un destino OSC"""
    host: str
    port: int
    name: str = field(default="")
    enabled: bool = field(default=True)
    use_bundles: bool = field(default=True)
    send_names: bool = field(default=True)
    max_retries: int = field(default=3)
    retry_delay: float = field(default=0.1)
    
    def __post_init__(self):
        # Generar nombre automático si no se proporciona
        if not self.name:
            self.name = f"{self.host}:{self.port}"
            
        # Validar puerto
        if not 1 <= self.port <= 65535:
            raise ValueError(f"Puerto inválido: {self.port}")
            
        # Intentar resolver el host
        try:
            socket.gethostbyname(self.host)
        except socket.error:
            logger.warning(f"No se puede resolver el host: {self.host}")
    
    def __str__(self):
        return f"OSCTarget({self.name} @ {self.host}:{self.port})"
    
    def __repr__(self):
        return self.__str__()


class SpatOSCBridge:
    """Puente OSC robusto y optimizado para Spat Revolution"""
    
    # Variable de clase para controlar warnings
    _bundle_warning_shown = False
    
    # Direcciones OSC de Spat Revolution
    OSC_PATHS = {
        'position_xyz': '/source/{}/xyz',
        'position_aed': '/source/{}/aed',
        'yaw': '/source/{}/yaw',
        'pitch': '/source/{}/pitch', 
        'roll': '/source/{}/roll',
        'aperture': '/source/{}/aperture',
        'name': '/source/{}/name',
        'gain': '/source/{}/gain',
        'mute': '/source/{}/mute',
        'solo': '/source/{}/solo'
    }
    
    def __init__(
        self,
        targets: Optional[List[Union[OSCTarget, Tuple[str, int]]]] = None,
        fps: int = 120,
        buffer_size: int = 2000,
        retry_on_error: bool = True,
        source_offset: int = 1,
        auto_reconnect: bool = True
    ):
        self.fps = fps
        self.dt = 1.0 / fps
        self.buffer_size = buffer_size
        self.retry_on_error = retry_on_error
        self.source_offset = source_offset
        self.auto_reconnect = auto_reconnect
        
        # Configurar destinos de forma robusta
        self.targets: List[OSCTarget] = []
        self._clients: Dict[str, Any] = {}
        self._failed_targets: Dict[str, float] = {}  # Para reconexión automática
        
        # Procesar targets de entrada
        if targets is None:
            targets = [OSCTarget("127.0.0.1", 9000)]
        
        for target in targets:
            self._add_target_safe(target)
        
        # Buffer y cache
        self._message_buffer = deque(maxlen=buffer_size)
        self._name_cache: Dict[int, str] = {}
        
        # Estadísticas mejoradas
        self._stats = {
            "messages_sent": 0,
            "messages_failed": 0,
            "bundles_sent": 0,
            "parameters_sent": {
                "positions": 0,
                "orientations": 0,
                "apertures": 0,
                "names": 0
            },
            "last_error": None,
            "start_time": time.time(),
            "reconnection_attempts": 0,
            "active_targets": len([t for t in self.targets if t.enabled])
        }
        
        logger.info(f"SpatOSCBridge inicializado con {len(self.targets)} destinos")
        
    def _add_target_safe(self, target: Union[OSCTarget, Tuple[str, int]]):
        """Añadir target de forma segura con validación"""
        try:
            # Convertir tupla a OSCTarget si es necesario
            if isinstance(target, tuple) and len(target) >= 2:
                host, port = target[0], target[1]
                name = target[2] if len(target) > 2 else f"{host}:{port}"
                osc_target = OSCTarget(host, port, name)
                self.targets.append(osc_target)
                self._create_client_safe(osc_target)
                
            elif isinstance(target, OSCTarget):
                self.targets.append(target)
                self._create_client_safe(target)
                
            else:
                logger.warning(f"Target inválido ignorado: {target} (tipo: {type(target)})")
                
        except Exception as e:
            logger.error(f"Error añadiendo target {target}: {e}")
            
    def _create_client_safe(self, target: OSCTarget):
        """Crear cliente OSC de forma segura"""
        if not target.enabled:
            return
            
        try:
            if _OSC_AVAILABLE:
                client = udp_client.SimpleUDPClient(target.host, target.port)
            else:
                client = MockUDPClient(target.host, target.port)
                
            self._clients[target.name] = client
            logger.info(f"Cliente OSC creado para {target}")
            
        except Exception as e:
            logger.error(f"Error creando cliente para {target}: {e}")
            target.enabled = False
            self._failed_targets[target.name] = time.time()
            
    def add_target(self, target: Union[OSCTarget, Tuple[str, int]]):
        """Añadir un nuevo destino OSC dinámicamente"""
        self._add_target_safe(target)
        self._stats["active_targets"] = len([t for t in self.targets if t.enabled])
        
    def remove_target(self, name: str):
        """Eliminar un destino OSC"""
        self.targets = [t for t in self.targets if t.name != name]
        if name in self._clients:
            del self._clients[name]
        if name in self._failed_targets:
            del self._failed_targets[name]
        self._stats["active_targets"] = len([t for t in self.targets if t.enabled])
        logger.info(f"Target {name} eliminado")
        
    def _send_message(self, address: str, values: list, target: OSCTarget):
        """Enviar mensaje OSC a un target específico"""
        if not target.enabled:
            return
            
        client = self._clients.get(target.name)
        if not client:
            # Intentar crear cliente si no existe
            self._create_client_safe(target)
            client = self._clients.get(target.name)
            
        if client:
            try:
                client.send_message(address, values)
                self._stats["messages_sent"] += 1
            except Exception as e:
                logger.error(f"Error enviando a {address}: {e}")
                self._stats["messages_failed"] += 1
                self._stats["last_error"] = str(e)
                
                # Marcar target como fallido para reconexión
                if self.auto_reconnect:
                    target.enabled = False
                    self._failed_targets[target.name] = time.time()
    
    
    def send_full_state(
        self,
        positions: np.ndarray,
        orientations: Optional[np.ndarray] = None,
        apertures: Optional[np.ndarray] = None,
        names: Optional[Dict[int, str]] = None,
        timestamp: Optional[float] = None
    ):
        """
        Enviar estado completo con manejo robusto de errores
        
        Parameters
        ----------
        positions : np.ndarray
            Array (N, 3) con posiciones XYZ
        orientations : np.ndarray, optional
            Array (N, 3) con yaw, pitch, roll en radianes
        apertures : np.ndarray, optional
            Array (N,) con valores de aperture (0-1)
        names : dict, optional
            Diccionario {source_id: name}
        timestamp : float, optional
            Timestamp OSC
        """
        if timestamp is None:
            timestamp = time.time()
            
        # Validación de entrada
        if not isinstance(positions, np.ndarray):
            positions = np.array(positions)
            
        n_sources = len(positions)
        
        # Validar arrays opcionales
        if orientations is not None:
            if not isinstance(orientations, np.ndarray):
                orientations = np.array(orientations)
            if len(orientations) != n_sources:
                logger.error(f"Tamaño de orientations ({len(orientations)}) no coincide con positions ({n_sources})")
                orientations = None
                
        if apertures is not None:
            if not isinstance(apertures, np.ndarray):
                apertures = np.array(apertures)
            if len(apertures) != n_sources:
                logger.error(f"Tamaño de apertures ({len(apertures)}) no coincide con positions ({n_sources})")
                apertures = None
        
        # Procesar nombres nuevos/cambiados
        if names:
            for sid, name in names.items():
                if self._name_cache.get(sid) != name:
                    self._name_cache[sid] = name
        
        # Intentar reconectar targets fallidos si está habilitado
        if self.auto_reconnect:
            self._attempt_reconnections()
        
        # Enviar a cada destino activo
        for target in self.targets:
            # Verificación robusta del tipo
            if not isinstance(target, OSCTarget):
                logger.error(f"Target inválido encontrado: {target} (tipo: {type(target)})")
                continue
                
            if not target.enabled:
                continue
                
            client = self._clients.get(target.name)
            if client is None:
                logger.debug(f"Cliente no encontrado para {target.name}")
                continue
                
            # Enviar con reintentos si está configurado
            retries = target.max_retries if self.retry_on_error else 1
            
            for attempt in range(retries):
                try:
                    if target.use_bundles:
                        self._send_as_bundle(
                            client, target, positions, orientations, 
                            apertures, names, timestamp
                        )
                    else:
                        self._send_individual_messages(
                            client, target, positions, orientations,
                            apertures, names
                        )
                    break  # Éxito, salir del loop de reintentos
                    
                except Exception as e:
                    if attempt < retries - 1:
                        logger.warning(f"Intento {attempt + 1}/{retries} falló para {target.name}: {e}")
                        if target.retry_delay > 0:
                            time.sleep(target.retry_delay)
                    else:
                        self._handle_send_error(target, e)
                        
    def _send_as_bundle(
        self, client, target: OSCTarget, positions: np.ndarray, 
        orientations: Optional[np.ndarray], apertures: Optional[np.ndarray],
        names: Optional[Dict[int, str]], timestamp: float
    ):
        """Enviar datos como bundle OSC (optimizado)"""
        if not _OSC_AVAILABLE:
            if not self._bundle_warning_shown:
                logger.warning("Bundles OSC no disponibles en modo simulación")
                self._bundle_warning_shown = True
            return
            
        try:
            # Verificar si el cliente soporta bundles
            if not hasattr(client, 'send_bundle'):
                logger.debug(f"Cliente no soporta bundles, usando mensajes individuales")
                # Fallback a mensajes individuales
                self._send_individual_messages(client, target, positions, orientations, apertures, names)
                return
                
            bundle = OscBundleBuilder(timestamp)
            
            for i in range(len(positions)):
                source_index = i + self.source_offset
                
                # Posición
                msg = OscMessageBuilder(address=self.OSC_PATHS['position_xyz'].format(source_index))
                msg.add_arg(float(positions[i, 0]))
                msg.add_arg(float(positions[i, 1]))
                msg.add_arg(float(positions[i, 2]))
                bundle.add_content(msg.build())
                
                # Orientación si está disponible
                if orientations is not None:
                    # Yaw
                    msg = OscMessageBuilder(address=self.OSC_PATHS['yaw'].format(source_index))
                    msg.add_arg(float(np.degrees(orientations[i, 0])))
                    bundle.add_content(msg.build())
                    
                    # Pitch
                    msg = OscMessageBuilder(address=self.OSC_PATHS['pitch'].format(source_index))
                    msg.add_arg(float(np.degrees(orientations[i, 1])))
                    bundle.add_content(msg.build())
                    
                    # Roll
                    msg = OscMessageBuilder(address=self.OSC_PATHS['roll'].format(source_index))
                    msg.add_arg(float(np.degrees(orientations[i, 2])))
                    bundle.add_content(msg.build())
                
                # Aperture si está disponible
                if apertures is not None:
                    msg = OscMessageBuilder(address=self.OSC_PATHS['aperture'].format(source_index))
                    msg.add_arg(float(10.0 + (apertures[i] * 170.0)))  # 0-1 -> 10-180 deg
                    bundle.add_content(msg.build())
                
                # Nombre si ha cambiado
                if target.send_names and names and i in names:
                    if self._name_cache.get(i) != names[i]:
                        msg = OscMessageBuilder(address=self.OSC_PATHS['name'].format(source_index))
                        msg.add_arg(str(names[i]))
                        bundle.add_content(msg.build())
            
            client.send_bundle(bundle.build())
            self._stats["bundles_sent"] += 1
            self._stats["messages_sent"] += len(positions) * 3
            
        except AttributeError as e:
            if 'send_bundle' in str(e):
                # Si el error es específicamente sobre send_bundle, cambiar a mensajes individuales
                logger.info(f"Cambiando a mensajes individuales para {target.name}")
                target.use_bundles = False  # Desactivar bundles para este target
                self._send_individual_messages(client, target, positions, orientations, apertures, names)
            else:
                raise
        except Exception as e:
            logger.error(f"Error enviando bundle: {e}")
            raise
            
    def _send_individual_messages(
        self, client, target: OSCTarget, positions: np.ndarray,
        orientations: Optional[np.ndarray], apertures: Optional[np.ndarray],
        names: Optional[Dict[int, str]]
    ):
        """Enviar mensajes individuales (más compatible)"""
        try:
            for i in range(len(positions)):
                source_index = i + self.source_offset
                
                # Posición XYZ
                client.send_message(
                    self.OSC_PATHS['position_xyz'].format(source_index),
                    [float(positions[i, 0]), float(positions[i, 1]), float(positions[i, 2])]
                )
                self._stats["parameters_sent"]["positions"] += 1
                
                # Orientación si está disponible
                if orientations is not None:
                    client.send_message(
                        self.OSC_PATHS['yaw'].format(source_index),
                        float(np.degrees(orientations[i, 0]))
                    )
                    client.send_message(
                        self.OSC_PATHS['pitch'].format(source_index),
                        float(np.degrees(orientations[i, 1]))
                    )
                    client.send_message(
                        self.OSC_PATHS['roll'].format(source_index),
                        float(np.degrees(orientations[i, 2]))
                    )
                    self._stats["parameters_sent"]["orientations"] += 3
                
                # Aperture si está disponible
                if apertures is not None:
                    client.send_message(
                        self.OSC_PATHS['aperture'].format(source_index),
                        float(10.0 + (float(apertures[i]) * 170.0))
                    )
                    self._stats["parameters_sent"]["apertures"] += 1
                
                # Nombre si está disponible y ha cambiado
                if target.send_names and names and i in names:
                    if self._name_cache.get(i) != names[i]:
                        client.send_message(
                            self.OSC_PATHS['name'].format(source_index),
                            str(names[i])
                        )
                        self._stats["parameters_sent"]["names"] += 1
                        
                self._stats["messages_sent"] += 1
                
        except Exception as e:
            logger.error(f"Error enviando mensajes individuales: {e}")
            raise
            
    def _handle_send_error(self, target: OSCTarget, error: Exception):
        """Manejar errores de envío de forma inteligente"""
        logger.error(f"Error enviando a {target.name}: {error}")
        self._stats["messages_failed"] += 1
        self._stats["last_error"] = str(error)
        
        # Desactivar temporalmente si hay muchos errores
        error_threshold = 100
        if self._stats["messages_failed"] > error_threshold:
            target.enabled = False
            self._failed_targets[target.name] = time.time()
            logger.warning(f"Target {target.name} desactivado por exceso de errores ({error_threshold})")
            self._stats["active_targets"] = len([t for t in self.targets if t.enabled])
            
    def _attempt_reconnections(self):
        """Intentar reconectar targets fallidos"""
        current_time = time.time()
        reconnect_delay = 30.0  # Segundos antes de intentar reconectar
        
        for target in self.targets:
            if not target.enabled and target.name in self._failed_targets:
                if current_time - self._failed_targets[target.name] > reconnect_delay:
                    logger.info(f"Intentando reconectar {target.name}...")
                    target.enabled = True
                    self._create_client_safe(target)
                    
                    if target.enabled:
                        del self._failed_targets[target.name]
                        self._stats["reconnection_attempts"] += 1
                        self._stats["active_targets"] = len([t for t in self.targets if t.enabled])
                        logger.info(f"Reconexión exitosa para {target.name}")
                        
    async def send_full_state_async(self, *args, **kwargs):
        """Versión asíncrona de send_full_state"""
        await asyncio.get_running_loop().run_in_executor(
            None, self.send_full_state, *args, **kwargs
        )

    def send_source_name(self, source_id: int, name: str):
        """Enviar solo el nombre de una fuente"""
        source_index = source_id + self.source_offset
        
        for target in self.targets:
            if not isinstance(target, OSCTarget) or not target.enabled or not target.send_names:
                continue
                
            client = self._clients.get(target.name)
            if client:
                try:
                    client.send_message(
                        self.OSC_PATHS['name'].format(source_index),
                        str(name)
                    )
                    self._name_cache[source_id] = name
                    self._stats["parameters_sent"]["names"] += 1
                except Exception as e:
                    logger.error(f"Error enviando nombre: {e}")
                    

    def send_position(self, source_id: int, position: np.ndarray, active: bool = True):
        """Enviar posición de una fuente"""
        if not active or not self._check_rate_limit():
            return
            
        # Convertir a lista si es necesario
        if isinstance(position, np.ndarray):
            pos_list = position.tolist()
        else:
            pos_list = list(position)
            
        # Asegurar que tiene 3 elementos
        while len(pos_list) < 3:
            pos_list.append(0.0)
            
        for target in self.targets:
            if target.enabled:
                try:
                    spat_id = source_id + self.source_offset
                    address = f"/source/{spat_id}/xyz"
                    
                    client = self._clients.get(target.name)
                    if client:
                        client.send_message(address, [float(pos_list[0]), float(pos_list[1]), float(pos_list[2])])
                        self._stats["messages_sent"] += 1
                        
                        if 'positions' not in self._stats['parameters_sent']:
                            self._stats['parameters_sent']['positions'] = 0
                        self._stats['parameters_sent']['positions'] += 1
                        
                except Exception as e:
                    logger.error(f"Error enviando posición: {e}")
                    self._stats["messages_failed"] += 1


    def _check_rate_limit(self) -> bool:
        """Verificar si se debe enviar actualización OSC (para limitar tasa)"""
        # Por ahora, siempre enviar. Puedes implementar un limitador más sofisticado
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas detalladas"""
        pass  # TODO: Implementar
        uptime = time.time() - self._stats["start_time"]
        
        return {
        "messages_sent": self._stats["messages_sent"],
        "messages_failed": self._stats["messages_failed"],
        "bundles_sent": self._stats["bundles_sent"],
        "parameters_sent": self._stats["parameters_sent"].copy(),
        "last_error": self._stats["last_error"],
        "uptime_seconds": uptime,
        "active_targets": self._stats["active_targets"],
        "reconnection_attempts": self._stats["reconnection_attempts"]
        }
        uptime = time.time() - self._stats["start_time"]
        rate = self._stats["messages_sent"] / uptime if uptime > 0 else 0
        
        return {
        **self._stats,
        "uptime_seconds": uptime,
        "uptime_formatted": self._format_duration(uptime),
        "message_rate": rate,
        "active_targets": len([t for t in self.targets if t.enabled]),
        "total_targets": len(self.targets),
        "buffer_size": len(self._message_buffer),
        "cached_names": len(self._name_cache),
        "failed_targets": list(self._failed_targets.keys()),
        "success_rate": (1 - self._stats["messages_failed"] / max(1, self._stats["messages_sent"])) * 100
        }
        
    def _format_duration(self, seconds: float) -> str:
        """Formatear duración en formato legible"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        
    def reset_stats(self):
        """Resetear estadísticas"""
        self._stats["messages_sent"] = 0
        self._stats["messages_failed"] = 0
        self._stats["bundles_sent"] = 0
        self._stats["parameters_sent"] = {
            "positions": 0,
            "orientations": 0,
            "apertures": 0,
            "names": 0
        }
        self._stats["last_error"] = None
        self._stats["start_time"] = time.time()
        self._stats["reconnection_attempts"] = 0
        logger.info("Estadísticas reseteadas")
        
    def set_source_offset(self, offset: int):
        """Cambiar el offset de índice de fuentes"""
        self.source_offset = offset
        logger.info(f"Source offset cambiado a {offset}")
        
    def clear_name_cache(self):
        """Limpiar cache de nombres"""
        self._name_cache.clear()
        logger.info("Cache de nombres limpiado")
        
    def close(self):
        """Cerrar conexiones y limpiar recursos"""
        for target in self.targets:
            target.enabled = False
        self._clients.clear()
        self._message_buffer.clear()
        self._name_cache.clear()
        logger.info("SpatOSCBridge cerrado")
        
    def __enter__(self):
        """Context manager entrada"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager salida"""
        self.close()
        
    def __repr__(self):
        return f"SpatOSCBridge(targets={len(self.targets)}, fps={self.fps}, active={self._stats['active_targets']})"
    def send_orientation(self, source_id: int, yaw: float, pitch: float, roll: float):
        """Enviar orientación de una fuente"""
        if not self._check_rate_limit():
            return
            
        # Convertir a grados y asegurar que sean float de Python
        try:
            # Convertir a float de Python (no numpy)
            yaw_deg = float(np.degrees(float(yaw)))
            pitch_deg = float(np.degrees(float(pitch)))
            roll_deg = float(np.degrees(float(roll)))
        except (TypeError, ValueError):
            # Valores por defecto si hay error
            yaw_deg = 0.0
            pitch_deg = 0.0
            roll_deg = 0.0
        
        for target in self.targets:
            if target.enabled:
                try:
                    spat_id = source_id + self.source_offset
                    client = self._clients.get(target.name)
                    
                    if client:
                        # Enviar cada parámetro como float de Python
                        client.send_message(f"/source/{spat_id}/yaw", float(yaw_deg))
                        client.send_message(f"/source/{spat_id}/pitch", float(pitch_deg))
                        client.send_message(f"/source/{spat_id}/roll", float(roll_deg))
                        
                        self._stats["messages_sent"] += 3
                        
                        if 'orientations' not in self._stats['parameters_sent']:
                            self._stats['parameters_sent']['orientations'] = 0
                        self._stats['parameters_sent']['orientations'] += 1
                        
                except Exception as e:
                    logger.error(f"Error enviando orientación: {e}")
                    self._stats["messages_failed"] += 1


    def send_aperture(self, source_id: int, aperture: float):
        """Enviar apertura/directividad de una fuente"""
        if not self._check_rate_limit():
            return
            
        # Convertir a formato Spat y asegurar que sea float de Python
        try:
            # Convertir apertura de 0-1 a 10-180 grados (rango de Spat)
            # 0.0 -> 10°  (muy directivo)
            # 1.0 -> 180° (omnidireccional)
            aperture_deg = float(10.0 + (aperture * 170.0))
        except (TypeError, ValueError):
            aperture_deg = 90.0
        
        for target in self.targets:
            if target.enabled:
                try:
                    spat_id = source_id + self.source_offset
                    client = self._clients.get(target.name)
                    
                    if client:
                        client.send_message(f"/source/{spat_id}/aperture", float(aperture_deg))
                        self._stats["messages_sent"] += 1
                        
                        if 'apertures' not in self._stats['parameters_sent']:
                            self._stats['parameters_sent']['apertures'] = 0
                        self._stats['parameters_sent']['apertures'] += 1
                        
                except Exception as e:
                    logger.error(f"Error enviando apertura: {e}")
                    self._stats["messages_failed"] += 1


    def send_source_mute(self, source_id: int, muted: bool):
        """Enviar estado mute de una fuente"""
        for target in self.targets:
            if target.enabled:
                try:
                    spat_id = source_id + self.source_offset
                    # SPAT usa 0/1 para mute
                    mute_value = 1 if muted else 0
                    self._send_message(f"/source/{spat_id}/mute", [mute_value], target)
                    
                except Exception as e:
                    logger.error(f"Error enviando mute: {e}")


    
    def create_group(self, group_id: str, group_name: str):
        """Crear un grupo/macro en Spat."""
        try:
            group_name = str(group_name)  # Asegurar tipo string
            
            for target in self.targets:
                # Usar client para enviar
                if hasattr(self, 'client'):
                    self.client.send_message("/group/new", [group_name], target.host, target.port)
                else:
                    # Fallback si no hay client
                    self.send_message("/group/new", [group_name])
            
            print(f"   ✅ Grupo '{group_name}' creado via OSC")
            
        except Exception as e:
            print(f"   ❌ Error creando grupo: {e}")
    
    def add_source_to_group(self, source_id: int, group_name: str):
        """Añadir una fuente a un grupo en Spat."""
        try:
            source_id = int(source_id)  # Asegurar tipo int
            group_name = str(group_name)  # Asegurar tipo string
            
            for target in self.targets:
                if hasattr(self, 'client'):
                    self.client.send_message(
                        f"/source/{source_id}/group", 
                        [group_name], 
                        target.host, 
                        target.port
                    )
                else:
                    self.send_message(f"/source/{source_id}/group", [group_name])
                    
        except Exception as e:
            print(f"   ❌ Error añadiendo fuente al grupo: {e}")


    def send_macro_state(self, macro_name: str, source_ids: List[int], all_source_ids: List[int]):
        """Enviar estado completo de un macro a SPAT"""
        # Crear grupo para el macro
        self.create_group(macro_name, source_ids)
        
        # Configurar nombres y estados de todas las fuentes
        for i, sid in enumerate(source_ids):
            # Nombre con sufijo numérico
            source_name = f"{macro_name}_{i+1}"
            self.send_source_name(sid, source_name)
            self.send_source_mute(sid, False)  # Activar fuentes del macro
        
        # Desactivar fuentes que no están en el macro
        for sid in all_source_ids:
            if sid not in source_ids:
                self.send_source_name(sid, f"inactive_{sid}")
                self.send_source_mute(sid, True)  # Mutear fuentes inactivas
    def send_source_name(self, source_id: int, name: str):
        """Enviar solo el nombre de una fuente"""
        source_index = source_id + self.source_offset
        
        for target in self.targets:
            if not isinstance(target, OSCTarget) or not target.enabled or not target.send_names:
                continue
                
            client = self._clients.get(target.name)
            if client:
                try:
                    client.send_message(
                        self.OSC_PATHS['name'].format(source_index),
                        str(name)
                    )
                    self._name_cache[source_id] = name
                    self._stats["parameters_sent"]["names"] += 1
                except Exception as e:
                    logger.error(f"Error enviando nombre: {e}")
                    

    def send_position(self, source_id: int, position: np.ndarray, active: bool = True):
        """Enviar posición de una fuente"""
        if not active or not self._check_rate_limit():
            return
            
        # Convertir a lista si es necesario
        if isinstance(position, np.ndarray):
            pos_list = position.tolist()
        else:
            pos_list = list(position)
            
        # Asegurar que tiene 3 elementos
        while len(pos_list) < 3:
            pos_list.append(0.0)
            
        for target in self.targets:
            if target.enabled:
                try:
                    spat_id = source_id + self.source_offset
                    address = f"/source/{spat_id}/xyz"
                    
                    client = self._clients.get(target.name)
                    if client:
                        client.send_message(address, [float(pos_list[0]), float(pos_list[1]), float(pos_list[2])])
                        self._stats["messages_sent"] += 1
                        
                        if 'positions' not in self._stats['parameters_sent']:
                            self._stats['parameters_sent']['positions'] = 0
                        self._stats['parameters_sent']['positions'] += 1
                        
                except Exception as e:
                    logger.error(f"Error enviando posición: {e}")
                    self._stats["messages_failed"] += 1


    def _check_rate_limit(self) -> bool:
        """Verificar si se debe enviar actualización OSC (para limitar tasa)"""
        # Por ahora, siempre enviar. Puedes implementar un limitador más sofisticado
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas detalladas"""
        pass  # TODO: Implementar
        uptime = time.time() - self._stats["start_time"]
        
        return {
        "messages_sent": self._stats["messages_sent"],
        "messages_failed": self._stats["messages_failed"],
        "bundles_sent": self._stats["bundles_sent"],
        "parameters_sent": self._stats["parameters_sent"].copy(),
        "last_error": self._stats["last_error"],
        "uptime_seconds": uptime,
        "active_targets": self._stats["active_targets"],
        "reconnection_attempts": self._stats["reconnection_attempts"]
        }
        uptime = time.time() - self._stats["start_time"]
        rate = self._stats["messages_sent"] / uptime if uptime > 0 else 0
        
        return {
        **self._stats,
        "uptime_seconds": uptime,
        "uptime_formatted": self._format_duration(uptime),
        "message_rate": rate,
        "active_targets": len([t for t in self.targets if t.enabled]),
        "total_targets": len(self.targets),
        "buffer_size": len(self._message_buffer),
        "cached_names": len(self._name_cache),
        "failed_targets": list(self._failed_targets.keys()),
        "success_rate": (1 - self._stats["messages_failed"] / max(1, self._stats["messages_sent"])) * 100
        }
        
    def _format_duration(self, seconds: float) -> str:
        """Formatear duración en formato legible"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        
    def reset_stats(self):
        """Resetear estadísticas"""
        self._stats["messages_sent"] = 0
        self._stats["messages_failed"] = 0
        self._stats["bundles_sent"] = 0
        self._stats["parameters_sent"] = {
            "positions": 0,
            "orientations": 0,
            "apertures": 0,
            "names": 0
        }
        self._stats["last_error"] = None
        self._stats["start_time"] = time.time()
        self._stats["reconnection_attempts"] = 0
        logger.info("Estadísticas reseteadas")
        
    def set_source_offset(self, offset: int):
        """Cambiar el offset de índice de fuentes"""
        self.source_offset = offset
        logger.info(f"Source offset cambiado a {offset}")
        
    def clear_name_cache(self):
        """Limpiar cache de nombres"""
        self._name_cache.clear()
        logger.info("Cache de nombres limpiado")
        
    def close(self):
        """Cerrar conexiones y limpiar recursos"""
        for target in self.targets:
            target.enabled = False
        self._clients.clear()
        self._message_buffer.clear()
        self._name_cache.clear()
        logger.info("SpatOSCBridge cerrado")
        
    def __enter__(self):
        """Context manager entrada"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager salida"""
        self.close()
        
    def __repr__(self):
        return f"SpatOSCBridge(targets={len(self.targets)}, fps={self.fps}, active={self._stats['active_targets']})"
    def send_orientation(self, source_id: int, yaw: float, pitch: float, roll: float):
        """Enviar orientación de una fuente"""
        if not self._check_rate_limit():
            return
            
        # Convertir a grados y asegurar que sean float de Python
        try:
            # Convertir a float de Python (no numpy)
            yaw_deg = float(np.degrees(float(yaw)))
            pitch_deg = float(np.degrees(float(pitch)))
            roll_deg = float(np.degrees(float(roll)))
        except (TypeError, ValueError):
            # Valores por defecto si hay error
            yaw_deg = 0.0
            pitch_deg = 0.0
            roll_deg = 0.0
        
        for target in self.targets:
            if target.enabled:
                try:
                    spat_id = source_id + self.source_offset
                    client = self._clients.get(target.name)
                    
                    if client:
                        # Enviar cada parámetro como float de Python
                        client.send_message(f"/source/{spat_id}/yaw", float(yaw_deg))
                        client.send_message(f"/source/{spat_id}/pitch", float(pitch_deg))
                        client.send_message(f"/source/{spat_id}/roll", float(roll_deg))
                        
                        self._stats["messages_sent"] += 3
                        
                        if 'orientations' not in self._stats['parameters_sent']:
                            self._stats['parameters_sent']['orientations'] = 0
                        self._stats['parameters_sent']['orientations'] += 1
                        
                except Exception as e:
                    logger.error(f"Error enviando orientación: {e}")
                    self._stats["messages_failed"] += 1


    def send_aperture(self, source_id: int, aperture: float):
        """Enviar apertura/directividad de una fuente"""
        if not self._check_rate_limit():
            return
            
        # Convertir a formato Spat y asegurar que sea float de Python
        try:
            aperture_deg = float(10.0 + (aperture * 170.0))  # 0-1 -> 10-180 degrees
        except (TypeError, ValueError):
            aperture_deg = 90.0
        
        for target in self.targets:
            if target.enabled:
                try:
                    spat_id = source_id + self.source_offset
                    client = self._clients.get(target.name)
                    
                    if client:
                        client.send_message(f"/source/{spat_id}/aperture", float(aperture_deg))
                        self._stats["messages_sent"] += 1
                        
                        if 'apertures' not in self._stats['parameters_sent']:
                            self._stats['parameters_sent']['apertures'] = 0
                        self._stats['parameters_sent']['apertures'] += 1
                        
                except Exception as e:
                    logger.error(f"Error enviando apertura: {e}")
                    self._stats["messages_failed"] += 1


    def send_source_mute(self, source_id: int, muted: bool):
        """Enviar estado mute de una fuente"""
        for target in self.targets:
            if target.enabled:
                try:
                    spat_id = source_id + self.source_offset
                    # SPAT usa 0/1 para mute
                    mute_value = 1 if muted else 0
                    self._send_message(f"/source/{spat_id}/mute", [mute_value], target)
                    
                except Exception as e:
                    logger.error(f"Error enviando mute: {e}")


    def create_group(self, group_name: str, source_ids: List[int]):
        """Crear un grupo en SPAT con las fuentes especificadas"""
        for target in self.targets:
            if target.enabled:
                try:
                    # Crear el grupo
                    self._send_message("/group/new", [group_name], target)
                    
                    # Añadir fuentes al grupo
                    for sid in source_ids:
                        spat_id = sid + self.source_offset
                        self._send_message(f"/group/{group_name}/source/add", [spat_id], target)
                    
                    logger.info(f"Grupo '{group_name}' creado con {len(source_ids)} fuentes")
                    
                except Exception as e:
                    logger.error(f"Error creando grupo: {e}")


    def send_macro_state(self, macro_name: str, source_ids: List[int], all_source_ids: List[int]):
        """Enviar estado completo de un macro a SPAT"""
        # Crear grupo para el macro
        self.create_group(macro_name, source_ids)
        
        # Configurar nombres y estados de todas las fuentes
        for i, sid in enumerate(source_ids):
            # Nombre con sufijo numérico
            source_name = f"{macro_name}_{i+1}"
            self.send_source_name(sid, source_name)
            self.send_source_mute(sid, False)  # Activar fuentes del macro
        
        # Desactivar fuentes que no están en el macro
        for sid in all_source_ids:
            if sid not in source_ids:
                self.send_source_name(sid, f"inactive_{sid}")
                self.send_source_mute(sid, True)  # Mutear fuentes inactivas