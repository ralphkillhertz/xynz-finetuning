#!/usr/bin/env python3
"""
Test mínimo del Interactive Controller con OSC
"""

import os
import sys
import time
import numpy as np

# Path setup
current_dir = os.getcwd()
if 'trajectory_hub' in current_dir:
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

# NO deshabilitar OSC
if 'DISABLE_OSC' in os.environ:
    del os.environ['DISABLE_OSC']

from trajectory_hub.core.enhanced_trajectory_engine import EnhancedTrajectoryEngine
from trajectory_hub.core.spat_osc_bridge import SpatOSCBridge, OSCTarget

print("\n🎮 INICIANDO CONTROLLER DE PRUEBA CON OSC\n")

# Crear engine
engine = EnhancedTrajectoryEngine(max_sources=32, fps=60)

# Crear y configurar OSC bridge
print("📡 Configurando OSC...")
osc_target = OSCTarget("127.0.0.1", 9000)  # Puerto estándar de Spat
osc_bridge = SpatOSCBridge(targets=[osc_target], fps=60)

# IMPORTANTE: Asignar bridge al engine
engine.osc_bridge = osc_bridge

print(f"   Target: {osc_target.host}:{osc_target.port}")
print("   ✅ OSC Bridge configurado")

# Crear algunos macros
print("\n🎯 Creando macros...")

macros = []
formations = ["line", "circle", "grid"]
for i, formation in enumerate(formations):
    macro_id = engine.create_macro(f"Macro_{formation}", 
                                   source_count=4, 
                                   formation=formation,
                                   spacing=3.0)
    macros.append(macro_id)
    print(f"   ✅ {macro_id} creado")
    
    # Enviar creación del grupo a Spat
    if hasattr(osc_bridge, 'send_message'):
        # Crear grupo en Spat
        osc_bridge.send_message(f"/group/create", [macro_id, f"Macro_{formation}"])

# Aplicar concentración al primer macro
print("\n🎯 Aplicando concentración...")
engine.set_macro_concentration(macros[0], 0.5)

# Ejecutar simulación
print("\n🔄 Ejecutando simulación con OSC...")
print("   (Presiona Ctrl+C para detener)\n")

try:
    frame = 0
    while True:
        # Step del engine (incluye envío OSC)
        state = engine.step()
        
        # Mostrar info cada 60 frames (1 segundo a 60fps)
        if frame % 60 == 0:
            active_sources = sum(1 for sid in engine._source_motions if sid < engine.max_sources)
            print(f"   Frame {frame}: {active_sources} fuentes activas, enviando OSC...")
        
        frame += 1
        time.sleep(1.0/60.0)  # 60 FPS
        
except KeyboardInterrupt:
    print("\n\n✅ Simulación detenida")
    print("\n📊 VERIFICA EN SPAT:")
    print("   - Las fuentes deberían estar visibles")
    print("   - Los grupos/macros deberían existir")
    print("   - El monitor OSC debería mostrar mensajes")
    print("   - La concentración debería funcionar en Macro_line")
