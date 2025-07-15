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
            for i, (x, y, z) in enumerate(positions):
                source_id = i + 1  # IDs empiezan en 1 para Spat
                # Asegurar que source_id está en rango válido
                if 0 <= source_id <= self.n_sources:
                    # Formato OSC correcto para Spat
                    address = f"/source/{source_id}/xyz"
                    
                    # Convertir a float para evitar problemas de tipo
                    x_val = float(x) if not np.isnan(x) else 0.0
                    y_val = float(y) if not np.isnan(y) else 0.0
                    z_val = float(z) if not np.isnan(z) else 0.0
                    
                    # Enviar mensaje OSC
                    self.client.send_message(address, [x_val, y_val, z_val])
                    
                    # Debug opcional
                    if source_id == 0:  # Solo mostrar primera fuente
                        print(f"📡 OSC: {address} → [{x_val:.2f}, {y_val:.2f}, {z_val:.2f}]")
                        
        except Exception as e:
            print(f"❌ Error enviando OSC: {e}")
            
    def send_source_parameter(self, source_id: int, param: str, value: float):
        """Envía parámetro individual a Spat"""
        if 0 <= source_id <= self.n_sources:
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
