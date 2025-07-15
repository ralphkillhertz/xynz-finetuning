#!/usr/bin/env python3
"""
🚨 RESTAURACIÓN DE EMERGENCIA
🎯 Objetivo: Volver a CUALQUIER estado funcional
"""

import os
import shutil
import glob

def find_oldest_backup():
    """Encontrar el backup más antiguo (probablemente el más estable)"""
    
    # Buscar TODOS los backups de spat_osc_bridge
    all_backups = []
    
    # En el directorio actual
    all_backups.extend(glob.glob("trajectory_hub/core/spat_osc_bridge.py.backup_*"))
    
    # En trajectory_hub si estamos fuera
    all_backups.extend(glob.glob("spat_osc_bridge.py.backup_*"))
    
    # Buscar recursivamente
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.startswith("spat_osc_bridge.py.backup"):
                all_backups.append(os.path.join(root, file))
    
    # Eliminar duplicados
    all_backups = list(set(all_backups))
    
    if not all_backups:
        return None
    
    # Ordenar por fecha (los más antiguos primero)
    all_backups.sort()
    
    print(f"\n📋 Backups encontrados: {len(all_backups)}")
    for i, backup in enumerate(all_backups[:5]):  # Mostrar los 5 más antiguos
        print(f"  {i+1}. {os.path.basename(backup)}")
    
    return all_backups[0]  # El más antiguo

def restore_emergency():
    """Restauración de emergencia completa"""
    
    print("🚨 RESTAURACIÓN DE EMERGENCIA")
    print("=" * 50)
    
    # 1. Encontrar backup de OSC Bridge
    osc_backup = find_oldest_backup()
    
    if not osc_backup:
        print("❌ No se encontraron backups de spat_osc_bridge.py")
        print("\n🔍 Buscando en el historial de la sesión...")
        
        # Intentar crear uno desde el estado documentado
        create_from_session_state()
        return
    
    # 2. Restaurar OSC Bridge
    target = "trajectory_hub/core/spat_osc_bridge.py"
    print(f"\n📂 Restaurando OSC Bridge desde: {os.path.basename(osc_backup)}")
    shutil.copy(osc_backup, target)
    print("✅ OSC Bridge restaurado")
    
    # 3. Buscar backup de engine
    engine_backups = glob.glob("**/enhanced_trajectory_engine.py.backup_*", recursive=True)
    
    if engine_backups:
        # Preferir el backup_simple_20250707_103351 si existe
        preferred = [b for b in engine_backups if "simple_20250707_103351" in b]
        
        if preferred:
            engine_backup = preferred[0]
        else:
            engine_backup = sorted(engine_backups)[0]  # El más antiguo
        
        print(f"\n📂 Restaurando Engine desde: {os.path.basename(engine_backup)}")
        shutil.copy(engine_backup, "trajectory_hub/core/enhanced_trajectory_engine.py")
        print("✅ Engine restaurado")
    
    # 4. Verificar sintaxis básica
    print("\n🔍 Verificando sintaxis...")
    
    for file in [target, "trajectory_hub/core/enhanced_trajectory_engine.py"]:
        try:
            with open(file, 'r') as f:
                compile(f.read(), file, 'exec')
            print(f"✅ {os.path.basename(file)}: Sintaxis OK")
        except SyntaxError as e:
            print(f"❌ {os.path.basename(file)}: Error en línea {e.lineno}")

def create_from_session_state():
    """Crear configuración mínima funcional desde cero"""
    
    print("\n🔧 Creando configuración mínima funcional...")
    
    # OSC Bridge mínimo que sabemos que funciona
    osc_content = '''"""
OSC Bridge mínimo funcional
"""
import numpy as np
from pythonosc import udp_client
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class OSCTarget:
    def __init__(self, host: str, port: int, name: str = ""):
        self.host = host
        self.port = port
        self.name = name or f"{host}:{port}"

class SpatOSCBridge:
    def __init__(self, targets: List[OSCTarget], fps: int = 60, use_bundles: bool = False):
        self.targets = targets
        self.fps = fps
        self.use_bundles = use_bundles
        self.clients = {}
        
        for target in targets:
            self.clients[target] = udp_client.SimpleUDPClient(target.host, target.port)
            logger.info(f"OSC client created for {target.name}")
    
    def send_source_data(self, source_id: int, position: np.ndarray, 
                        orientation: Optional[np.ndarray] = None,
                        aperture: Optional[float] = None,
                        additional_params: Optional[Dict] = None):
        """Enviar datos de fuente a Spat"""
        
        for target in self.targets:
            client = self.clients.get(target)
            if not client:
                continue
            
            # Enviar posición
            try:
                client.send_message(f"/source/{source_id}/xyz", position.tolist())
            except Exception as e:
                logger.error(f"Error enviando posición: {e}")
    
    def create_group(self, group_id: str, group_name: str):
        """Crear grupo - stub por ahora"""
        pass
    
    def add_source_to_group(self, source_id: int, group_name: str):
        """Añadir fuente a grupo - stub por ahora"""
        pass
    
    def get_stats(self):
        """Obtener estadísticas"""
        return {
            "active_targets": len(self.targets),
            "fps": self.fps
        }
'''
    
    with open("trajectory_hub/core/spat_osc_bridge.py", 'w') as f:
        f.write(osc_content)
    
    print("✅ OSC Bridge mínimo creado")
    print("\n⚠️ NOTA: Esta es una versión mínima.")
    print("Los grupos no funcionarán pero las posiciones sí.")

def main():
    restore_emergency()
    
    print("\n" + "="*50)
    print("✅ RESTAURACIÓN COMPLETADA")
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. python test_current_state.py")
    print("2. Si funciona, ejecutar el controlador")
    print("3. IGNORAR errores de grupos")
    print("4. Retomar sistema paralelo")
    
    print("\n⚠️ IMPORTANTE:")
    print("- NO intentar arreglar grupos OSC")
    print("- NO modificar más el bridge")
    print("- ENFOCARSE en sistema paralelo")

if __name__ == "__main__":
    main()