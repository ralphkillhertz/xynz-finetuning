# trajectory_hub/core/spat_osc_bridge.py
# FIX TEMPORAL: Asegurar envío OSC a Spat

import numpy as np
from pythonosc import udp_client, osc_server, dispatcher
import threading
import time
from typing import Dict, List, Tuple, Optional, Any, Callable
import logging


class OSCTarget:
    """Representa un destino OSC"""
    def __init__(self, host: str = "127.0.0.1", port: int = 9000, name: str = "default"):
        self.host = host
        self.port = port
        self.name = name
        self.client = udp_client.SimpleUDPClient(host, port)
    
    def send(self, address: str, *args):
        """Envía mensaje OSC"""
        self.client.send_message(address, args)

class SpatOSCBridge:
    """Bridge para comunicación OSC con Spat"""
    
    def __init__(self, send_port: int = 9000, receive_port: int = 9001, 
                 host: str = "127.0.0.1"):
        """Inicializa el bridge OSC"""
        self.host = host
        self.send_port = send_port
        self.receive_port = receive_port
        
        # Cliente OSC para enviar
        self.client = udp_client.SimpleUDPClient(self.host, self.send_port)
        
        # Servidor OSC para recibir
        self.dispatcher = dispatcher.Dispatcher()
        self.server = None
        self.server_thread = None
        
        # Estado
        self.is_running = False
        self.callbacks = {}
        
        # Configuración
        self.n_sources = 128
        self.update_rate = 60  # Hz
        
        print(f"✅ OSC Bridge inicializado - Enviando a {self.host}:{self.send_port}")
        
    def send_source_positions(self, positions: Dict[int, Tuple[float, float, float]]):
        """Envía posiciones de fuentes a Spat - FIX APLICADO"""
        try:
            for source_idx, (x, y, z) in positions.items():
                # source_idx viene de trajectory_hub (0-based), convertir a SPAT (1-based)
                source_id = source_idx + 1
                # Asegurar que source_id está en rango válido
                if 1 <= source_id <= self.n_sources:
                    # Formato OSC correcto para Spat
                    address = f"/source/{source_id}/xyz"
                    
                    # Convertir a float para evitar problemas de tipo
                    x_val = float(x) if not np.isnan(x) else 0.0
                    y_val = float(y) if not np.isnan(y) else 0.0
                    z_val = float(z) if not np.isnan(z) else 0.0
                    
                    # Enviar mensaje OSC
                    self.client.send_message(address, [x_val, y_val, z_val])
                    
                    # Debug opcional (comentado para evitar spam)
                    # if source_id == 1:  # Mostrar primera fuente (ahora es 1, no 0)
                    #     print(f"📡 OSC: {address} → [{x_val:.2f}, {y_val:.2f}, {z_val:.2f}]")
                        
        except Exception as e:
            print(f"❌ Error enviando OSC: {e}")
            
    def send_source_parameter(self, source_id: int, param: str, value: float):
        """Envía parámetro individual a Spat"""
        if 1 <= source_id <= self.n_sources:
            address = f"/source/{source_id}/{param}"
            self.client.send_message(address, float(value))
            
    def send_all_sources_positions(self, all_positions: List[Tuple[float, float, float]]):
        """Envía todas las posiciones de una vez"""
        positions_dict = {i: pos for i, pos in enumerate(all_positions[:self.n_sources])}
        self.send_source_positions(positions_dict)
        
    def send_macro_positions(self, macro_name: str, positions: List[Tuple[float, float, float]]):
        """Envía posiciones de un macro específico"""
        print(f"🎯 Enviando macro '{macro_name}' con {len(positions)} fuentes")
        self.send_all_sources_positions(positions)
    
    def set_source_name(self, source_id: int, name: str):
        """Establece el nombre de una fuente en SPAT"""
        if 1 <= source_id <= self.n_sources:
            address = f"/source/{source_id}/name"
            self.client.send_message(address, name)
            print(f"📝 Nombre de fuente {source_id}: '{name}'")
    
    def set_macro_source_names(self, macro_name: str, source_ids: List[int]):
        """Nombra las fuentes de un macro según el formato Macro_name_n"""
        print(f"📝 Nombrando {len(source_ids)} fuentes para macro '{macro_name}'")
        for i, source_id in enumerate(source_ids, 1):
            name = f"{macro_name}_{i}"
            self.set_source_name(source_id, name)
        print(f"📝 Completado nombramiento de fuentes")
    
    def enable_source(self, source_id: int, enabled: bool = True):
        """Activa o desactiva una fuente en SPAT"""
        if 1 <= source_id <= self.n_sources:
            address = f"/source/{source_id}/enable"
            # En SPAT: 1 = enabled, 0 = disabled
            value = 1 if enabled else 0
            self.client.send_message(address, value)
            status = "activada" if enabled else "desactivada"
            print(f"🔊 Fuente {source_id} {status}")
    
    def mute_source(self, source_id: int, muted: bool = True):
        """Mutea o desmutea una fuente en SPAT"""
        if 1 <= source_id <= self.n_sources:
            address = f"/source/{source_id}/mute"
            # CORRECCIÓN: En SPAT mute funciona normal: 1 = muted, 0 = unmuted
            value = 1 if muted else 0
            self.client.send_message(address, value)
            status = "muteada" if muted else "desmuteada"
            print(f"🔇 Fuente {source_id} {status}")
    
    def enable_macro_sources(self, source_ids: List[int], enabled: bool = True):
        """Activa o desactiva todas las fuentes de un macro"""
        for source_id in source_ids:
            self.enable_source(source_id, enabled)
    
    def select_sources(self, source_ids: List[int], selected: bool = True):
        """Selecciona o deselecciona fuentes en SPAT"""
        for source_id in source_ids:
            if 1 <= source_id <= self.n_sources:
                address = f"/source/{source_id}/select"
                value = 1 if selected else 0
                self.client.send_message(address, value)
        
        if selected:
            print(f"✓ {len(source_ids)} fuentes seleccionadas")
    
    def restore_default_names(self, source_ids: List[int]):
        """Restaura los nombres por defecto de las fuentes en SPAT"""
        for source_id in source_ids:
            if 1 <= source_id <= self.n_sources:
                default_name = f"Default {source_id}"
                self.set_source_name(source_id, default_name)
        print(f"📝 Nombres restaurados para {len(source_ids)} fuentes")
        
    def test_connection(self):
        """Prueba la conexión enviando un mensaje de test"""
        try:
            self.client.send_message("/test", 1.0)
            print(f"✅ Test OSC enviado a {self.host}:{self.send_port}")
            
            # Enviar una posición de prueba
            self.send_source_positions({0: (1.0, 0.0, 0.0)})
            print("✅ Posición de prueba enviada")
            
            return True
        except Exception as e:
            print(f"❌ Error en test de conexión: {e}")
            return False
            
    def start_server(self):
        """Inicia el servidor OSC para recibir mensajes"""
        if not self.is_running:
            self.server = osc_server.ThreadingOSCUDPServer(
                ("127.0.0.1", self.receive_port), 
                self.dispatcher
            )
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            self.is_running = True
            print(f"✅ Servidor OSC escuchando en puerto {self.receive_port}")
            
    def stop_server(self):
        """Detiene el servidor OSC"""
        if self.is_running and self.server:
            self.server.shutdown()
            self.is_running = False
            print("🛑 Servidor OSC detenido")
            
    def __del__(self):
        """Limpieza al destruir el objeto"""
        self.stop_server()
